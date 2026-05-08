#include <seastar/core/app-template.hh>
#include <seastar/core/future.hh>
#include <seastar/core/smp.hh>
#include <seastar/core/when_all.hh>
#include <seastar/core/file.hh>
#include <seastar/core/fstream.hh>
#include <seastar/core/seastar.hh>
#include <seastar/core/thread.hh>
#include <seastar/util/log.hh>

#include <boost/program_options.hpp>

#include <vector>
#include <string>
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <chrono>

#include "prime_sieve.hpp"

using namespace seastar;
namespace bpo = boost::program_options;

struct Task {
    uint64_t start;
    uint64_t end;
};

struct TaskResult {
    Task task;
    int core_id;
    std::vector<uint64_t> primes;

    TaskResult() = default;
    TaskResult(Task t, int cid, std::vector<uint64_t> p) noexcept
        : task(t), core_id(cid), primes(std::move(p)) {}
    TaskResult(TaskResult&&) noexcept = default;
    TaskResult& operator=(TaskResult&&) noexcept = default;
};

// 输出结果到 CSV：Seastar DMA I/O，按起点排序以保证稳定输出
future<void> save_to_csv(std::vector<TaskResult> results, std::string filename) {
    std::sort(results.begin(), results.end(),
              [](const TaskResult& a, const TaskResult& b) noexcept {
                  return a.task.start < b.task.start;
              });

    return seastar::async([filename = std::move(filename),
                            results = std::move(results)]() mutable {
        auto f = open_file_dma(filename,
                               open_flags::wo | open_flags::create | open_flags::truncate).get();
        file_output_stream_options opts;
        opts.buffer_size = 4 * 1024 * 1024;
        auto out = make_file_output_stream(std::move(f), opts).get();

        char tmp[32];
        std::string line;
        line.reserve(128 * 1024);

        auto append_u64 = [&](uint64_t v) {
            char* end = ::util::fast_uint64_to_str(v, tmp);
            line.append(tmp, end - tmp);
        };

        for (const auto& r : results) {
            line.clear();
            append_u64(r.task.start);
            line.push_back('-');
            append_u64(r.task.end);
            line.push_back(',');
            append_u64(static_cast<uint64_t>(r.core_id));
            for (uint64_t p : r.primes) {
                line.push_back(',');
                append_u64(p);
            }
            line.push_back('\n');
            out.write(line.data(), line.size()).get();
        }
        out.flush().get();
        out.close().get();
    });
}

int main(int argc, char** argv) {
    app_template app;

    app.add_options()
        ("tasks,t", bpo::value<int>()->default_value(20), "任务总数")
        ("chunk,n", bpo::value<int>()->default_value(100000), "每个任务的区间大小")
        ("output,o", bpo::value<std::string>()->default_value("gemma4_seastar_prime.csv"), "输出CSV文件路径");

    return app.run(argc, argv, [&app] {
        global_logger_registry().set_all_loggers_level(log_level::error);

        auto& config = app.configuration();
        int num_tasks = config["tasks"].as<int>();
        int chunk_size = config["chunk"].as<int>();
        std::string output_file = config["output"].as<std::string>();

        if (num_tasks <= 0) num_tasks = 20;
        if (chunk_size <= 0) chunk_size = 100000;

        uint64_t interval_size = static_cast<uint64_t>(chunk_size);
        uint64_t total_range = static_cast<uint64_t>(num_tasks) * interval_size;

        unsigned num_cores = smp::count;

        auto compute_start = std::chrono::steady_clock::now();

        // Round-Robin 静态分发：每核 1 次 submit_to，核内循环处理 i, i+N, i+2N, ...
        // 相对每任务一次 submit_to，调度/跨 shard 消息量从 O(num_tasks) 降至 O(num_cores)
        // 结果在所属 shard 上原地构建，未跨 shard 移动时不触发 cross-shard free
        std::vector<future<std::vector<TaskResult>>> per_core_futs;
        per_core_futs.reserve(num_cores);

        for (unsigned c = 0; c < num_cores; ++c) {
            per_core_futs.push_back(smp::submit_to(c,
                [c, num_cores, num_tasks, interval_size, total_range]() {
                    return seastar::async(
                        [c, num_cores, num_tasks, interval_size, total_range]() {
                            std::vector<TaskResult> bucket;
                            const size_t my_count =
                                (static_cast<size_t>(num_tasks) + num_cores - 1 - c) / num_cores;
                            bucket.reserve(my_count);
                            for (int i = static_cast<int>(c); i < num_tasks;
                                 i += static_cast<int>(num_cores)) {
                                uint64_t start = static_cast<uint64_t>(i) * interval_size + 2;
                                uint64_t nominal_end =
                                    static_cast<uint64_t>(i + 1) * interval_size + 1;
                                uint64_t end = std::min(nominal_end, total_range);
                                auto primes = prime::segmented_sieve(start, end + 1);
                                bucket.emplace_back(Task{start, end}, static_cast<int>(c),
                                                    std::move(primes));
                            }
                            return bucket;
                        });
                }));
        }

        return when_all_succeed(per_core_futs.begin(), per_core_futs.end()).then(
            [compute_start, output_file, num_tasks, chunk_size](
                std::vector<std::vector<TaskResult>> per_core_results) {
                auto compute_end = std::chrono::steady_clock::now();
                auto compute_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                    compute_end - compute_start).count();

                size_t total_count = 0;
                for (const auto& v : per_core_results) total_count += v.size();
                std::vector<TaskResult> all_results;
                all_results.reserve(total_count);
                uint64_t total_primes = 0;
                for (auto& v : per_core_results) {
                    for (auto& r : v) {
                        total_primes += r.primes.size();
                        all_results.push_back(std::move(r));
                    }
                }

                return save_to_csv(std::move(all_results), output_file)
                    .then([total_primes, compute_start, compute_ms, num_tasks, chunk_size] {
                        auto end_time = std::chrono::steady_clock::now();
                        auto total_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                            end_time - compute_start).count();
                        std::cout << "已完成任务: " << num_tasks << "/" << num_tasks << std::endl;
                        std::cout << "素数总数:   " << total_primes << std::endl;
                        std::cout << "区间大小:   " << chunk_size << std::endl;
                        std::cout << "计算耗时:   " << compute_ms << " ms" << std::endl;
                        std::cout << "总耗时:     " << total_ms << " ms" << std::endl;
                    });
            });
    });
}
