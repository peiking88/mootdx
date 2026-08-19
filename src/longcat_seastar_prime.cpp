// longcat_seastar_prime: 并行素数计算程序 - 使用 Seastar 框架
// 工作模式：集中式任务队列 + std::mutex 互斥分发
// Worker 从共享 std::queue 取任务，每次加锁弹出一个任务，计算后写回全局结果
// 与其他程序保持接口兼容：-t tasks -n chunk-size -c cores -o output.csv

#include <seastar/core/app-template.hh>
#include <seastar/core/future.hh>
#include <seastar/core/smp.hh>
#include <seastar/core/when_all.hh>
#include <seastar/core/loop.hh>
#include <seastar/core/file.hh>
#include <seastar/core/fstream.hh>
#include <seastar/core/seastar.hh>
#include <seastar/core/thread.hh>
#include <seastar/util/log.hh>
#include <boost/program_options.hpp>

#include <vector>
#include <queue>
#include <mutex>
#include <memory>
#include <iostream>
#include <iomanip>
#include <chrono>
#include <cstdint>
#include <algorithm>

#include "prime_sieve.hpp"

namespace po = boost::program_options;

static seastar::logger applog("longcat_prime");

// 任务结构体
struct PrimeTask {
    uint64_t start;
    uint64_t end;
    unsigned task_id;

    PrimeTask() : start(0), end(0), task_id(0) {}
    PrimeTask(uint64_t s, uint64_t e, unsigned id)
        : start(s), end(e), task_id(id) {}
};

// 任务结果结构体
struct TaskResult {
    uint64_t range_start;
    uint64_t range_end;
    unsigned task_id;
    unsigned cpu_id;
    std::vector<uint64_t> primes;

    TaskResult() : range_start(0), range_end(0), task_id(0), cpu_id(0) {}
    TaskResult(uint64_t s, uint64_t e, unsigned tid, unsigned cid, std::vector<uint64_t>&& p)
        : range_start(s), range_end(e), task_id(tid), cpu_id(cid), primes(std::move(p)) {}
};

// 集中式任务队列：所有 worker 通过互斥锁争抢任务
class TaskQueue {
    std::queue<PrimeTask> _queue;
    std::mutex _mutex;
public:
    void initialize(uint64_t range_start, uint64_t range_end, uint64_t interval_size) {
        std::lock_guard<std::mutex> lock(_mutex);
        _queue = std::queue<PrimeTask>();
        unsigned task_id = 0;
        for (uint64_t current = range_start; current < range_end; ) {
            uint64_t end = std::min(current + interval_size, range_end);
            _queue.emplace(current, end, task_id++);
            current = end;
        }
        applog.info("Initialized task queue with {} tasks", task_id);
    }

    // 弹出一个任务，返回是否成功
    bool pop(PrimeTask& task) {
        std::lock_guard<std::mutex> lock(_mutex);
        if (_queue.empty()) return false;
        task = _queue.front();
        _queue.pop();
        return true;
    }
};

// 全局结果存储
struct alignas(64) PaddedResults { std::vector<TaskResult> results; };
constexpr size_t kMaxCores = 128;
static PaddedResults g_shard_results[kMaxCores];

// 工作函数，每个CPU核心执行的任务
// 从集中式队列反复弹出一个任务（每次加锁），计算后写入 per-shard 结果
static seastar::future<> worker(TaskQueue* queue, unsigned cpu_id) {
    return seastar::repeat(
        [queue, cpu_id]() -> seastar::future<seastar::stop_iteration> {
            PrimeTask task{0, 0, 0};
            if (!queue->pop(task)) {
                return seastar::make_ready_future<seastar::stop_iteration>(seastar::stop_iteration::yes);
            }
            applog.debug("CPU {} processing range {}-{}", cpu_id, task.start, task.end);
            auto primes = prime::segmented_sieve(task.start, task.end);
            g_shard_results[cpu_id].results.emplace_back(
                task.start, task.end, task.task_id, cpu_id, std::move(primes));
            return seastar::make_ready_future<seastar::stop_iteration>(seastar::stop_iteration::no);
        }
    );
}

static seastar::future<> output_results(const std::string& filename,
                                         int num_tasks, int chunk_size,
                                         long compute_ms) {
    std::vector<TaskResult> all_results;
    size_t total_primes = 0;
    {
        size_t total = 0;
        unsigned num_cores = seastar::smp::count;
        for (size_t i = 0; i < num_cores; ++i) {
            total += g_shard_results[i].results.size();
        }
        all_results.reserve(total);
        for (size_t i = 0; i < num_cores; ++i) {
            for (auto& r : g_shard_results[i].results) {
                total_primes += r.primes.size();
                all_results.push_back(std::move(r));
            }
            g_shard_results[i].results.clear();
        }
    }

    std::sort(all_results.begin(), all_results.end(),
              [](const TaskResult& a, const TaskResult& b) {
                  return a.range_start < b.range_start;
              });

    std::cout << "\n========================================" << std::endl;
    std::cout << "         计算结果统计" << std::endl;
    std::cout << "========================================" << std::endl;
    std::cout << "已完成任务: " << all_results.size() << "/" << num_tasks << std::endl;
    std::cout << "素数总数:   " << total_primes << std::endl;
    std::cout << "区间大小:   " << chunk_size << std::endl;
    std::cout << "计算耗时:   " << compute_ms << " ms" << std::endl;

    uint64_t total_numbers = static_cast<uint64_t>(num_tasks) * chunk_size;
    if (total_numbers > 0) {
        double prime_density = 100.0 * total_primes / total_numbers;
        std::cout << "素数密度:   " << std::fixed << std::setprecision(4)
                  << prime_density << "%" << std::endl;
    }

    if (compute_ms > 0) {
        std::cout << "计算速度:   " << std::fixed << std::setprecision(0)
                  << static_cast<double>(total_numbers) / compute_ms << " 数/毫秒" << std::endl;
    }
    std::cout << "========================================" << std::endl;

    return seastar::async([filename, results = std::move(all_results)]() mutable {
        auto f = seastar::open_file_dma(filename,
            seastar::open_flags::wo | seastar::open_flags::create | seastar::open_flags::truncate).get();
        seastar::file_output_stream_options opts;
        opts.buffer_size = 4 * 1024 * 1024;
        auto out = seastar::make_file_output_stream(std::move(f), opts).get();

        char tmp[21];
        std::string line;
        line.reserve(128 * 1024);
        for (const auto& r : results) {
            line.clear();
            auto append_u64 = [&](uint64_t v) {
                char* end = util::fast_uint64_to_str(v, tmp);
                line.append(tmp, end - tmp);
            };
            append_u64(r.range_start);
            line.push_back('-');
            append_u64(r.range_end);
            line.push_back(',');
            append_u64(r.cpu_id);
            for (uint64_t prime : r.primes) {
                line.push_back(',');
                append_u64(prime);
            }
            line.push_back('\n');
            out.write(line.data(), line.size()).get();
        }
        out.flush().get();
        out.close().get();
    });
}

static seastar::future<> seastar_main(const po::variables_map& config) {
    applog.set_level(seastar::log_level::error);

    int num_tasks = config["tasks"].as<int>();
    int chunk_size = config["chunk"].as<int>();
    if (num_tasks <= 0) num_tasks = 20;
    if (chunk_size <= 0) chunk_size = 100000;

    if (config.count("log-level")) {
        std::string level = config["log-level"].as<std::string>();
        if (level == "debug") applog.set_level(seastar::log_level::debug);
        else if (level == "info") applog.set_level(seastar::log_level::info);
        else if (level == "trace") applog.set_level(seastar::log_level::trace);
    }

    std::string output_file = config.count("output")
        ? config["output"].as<std::string>()
        : "longcat_seastar_prime.csv";

    uint64_t range_start = 2;
    uint64_t range_end = static_cast<uint64_t>(num_tasks) * chunk_size;

    unsigned num_cores = seastar::smp::count;
    for (size_t i = 0; i < num_cores; ++i) {
        g_shard_results[i].results.clear();
    }

    std::cout << "\n========================================" << std::endl;
    std::cout << "任务队列初始化完成" << std::endl;
    std::cout << "========================================" << std::endl;
    std::cout << "计算范围: 2 - " << range_end << std::endl;
    std::cout << "总任务数: " << num_tasks << std::endl;
    std::cout << "区间大小: " << chunk_size << std::endl;
    std::cout << "CPU核心数: " << num_cores << std::endl;
    std::cout << "========================================\n" << std::endl;

    auto start_time = std::chrono::high_resolution_clock::now();

    return seastar::do_with(
        std::make_shared<TaskQueue>(),
        [num_tasks, chunk_size, range_start, range_end, output_file, start_time](std::shared_ptr<TaskQueue> queue) {
            queue->initialize(range_start, range_end, static_cast<uint64_t>(chunk_size));

            std::vector<seastar::future<>> workers;
            workers.reserve(seastar::smp::count);
            for (unsigned i = 0; i < seastar::smp::count; ++i) {
                workers.push_back(
                    seastar::smp::submit_to(i, [queue, i] {
                        return worker(queue.get(), i);
                    })
                );
            }

            return seastar::when_all(workers.begin(), workers.end()).then(
                [num_tasks, chunk_size, output_file, start_time](std::vector<seastar::future<>> results) mutable {
                    for (auto& f : results) {
                        if (f.failed()) {
                            return seastar::make_exception_future<>(f.get_exception());
                        }
                    }
                    auto compute_end = std::chrono::high_resolution_clock::now();
                    auto compute_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                        compute_end - start_time).count();

                    return output_results(output_file, num_tasks, chunk_size, compute_ms)
                        .then([start_time] {
                            auto total_end = std::chrono::high_resolution_clock::now();
                            auto total_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                                total_end - start_time).count();
                            std::cout << "总耗时:     " << total_ms << " ms" << std::endl;
                        });
                }
            );
        }
    );
}

int main(int argc, char** argv) {
    seastar::app_template app;

    app.add_options()
        ("tasks,t", po::value<int>()->default_value(20), "任务总数")
        ("chunk,n", po::value<int>()->default_value(100000), "每个任务的区间大小")
        ("output,o", po::value<std::string>()->default_value("output/longcat_seastar_prime.csv"), "输出CSV文件路径")
        ("log-level,l", po::value<std::string>(), "日志级别 (debug/info/error/trace)");

    return app.run(argc, argv, [&app] {
        return seastar_main(app.configuration());
    });
}
