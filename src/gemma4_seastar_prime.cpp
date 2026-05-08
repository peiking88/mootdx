#include <seastar/core/app-template.hh>
#include <seastar/core/future.hh>
#include <seastar/core/smp.hh>
#include <seastar/core/when_all.hh>
#include <seastar/core/file.hh>
#include <seastar/core/temporary_buffer.hh>
#include <seastar/core/seastar.hh>
#include <seastar/core/thread.hh>
#include <seastar/util/log.hh>

#include <boost/program_options.hpp>

#include <vector>
#include <string>
#include <algorithm>
#include <cstdint>
#include <cstring>
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

// 输出结果到 CSV：直接 dma_write + 双缓冲流式写入
// - 每个 4MiB 缓冲填满后异步发起 dma_write，同时切换到另一缓冲继续填充
// - 末尾不足一块时填零并 truncate 回真实大小，避免 file_output_stream 的状态机开销
// - 直接把 fast_uint64_to_str 写入对齐 DMA 缓冲，省掉 std::string 中间拷贝
future<void> save_to_csv(std::vector<TaskResult> results, std::string filename) {
    std::sort(results.begin(), results.end(),
              [](const TaskResult& a, const TaskResult& b) noexcept {
                  return a.task.start < b.task.start;
              });

    return seastar::async([filename = std::move(filename),
                            results = std::move(results)]() mutable {
        auto f = open_file_dma(filename,
                               open_flags::wo | open_flags::create | open_flags::truncate).get();

        const size_t mem_align = f.memory_dma_alignment();
        const size_t disk_align = f.disk_write_dma_alignment();
        constexpr size_t kBufSize = 4 * 1024 * 1024;  // 4 MiB，必为 disk_align 的整数倍
        static_assert((kBufSize & (kBufSize - 1)) == 0, "kBufSize must be power of 2");

        auto buf_a = seastar::temporary_buffer<char>::aligned(mem_align, kBufSize);
        auto buf_b = seastar::temporary_buffer<char>::aligned(mem_align, kBufSize);
        char* cur = buf_a.get_write();
        size_t cur_used = 0;
        uint64_t file_offset = 0;
        seastar::future<size_t> in_flight = seastar::make_ready_future<size_t>(size_t{0});
        bool using_a = true;

        // 仅在缓冲恰好写满时调用：此时整 kBufSize 都是有效数据，dma_write 安全
        auto flush_full_buffer = [&]() {
            in_flight.get();  // 等上次写入完成（保证另一缓冲安全可复用）
            char* base = using_a ? buf_a.get_write() : buf_b.get_write();
            in_flight = f.dma_write(file_offset, base, kBufSize);
            file_offset += kBufSize;
            using_a = !using_a;
            cur = using_a ? buf_a.get_write() : buf_b.get_write();
            cur_used = 0;
        };

        // 把任意长度字节序列写入双缓冲，跨边界时切片
        auto put_bytes = [&](const char* src, size_t n) {
            while (n > 0) {
                const size_t can = std::min(n, kBufSize - cur_used);
                std::memcpy(cur + cur_used, src, can);
                cur_used += can;
                src += can;
                n -= can;
                if (cur_used == kBufSize) [[unlikely]] flush_full_buffer();
            }
        };

        auto put_byte = [&](char c) {
            cur[cur_used++] = c;
            if (cur_used == kBufSize) [[unlikely]] flush_full_buffer();
        };

        // uint64 最长 20 字符：先写 stack tmp，再 put_bytes 处理跨边界
        auto put_u64 = [&](uint64_t v) {
            char tmp[20];
            char* end = ::util::fast_uint64_to_str(v, tmp);
            put_bytes(tmp, static_cast<size_t>(end - tmp));
        };

        for (const auto& r : results) {
            put_u64(r.task.start);
            put_byte('-');
            put_u64(r.task.end);
            put_byte(',');
            put_u64(static_cast<uint64_t>(r.core_id));
            for (uint64_t p : r.primes) {
                put_byte(',');
                put_u64(p);
            }
            put_byte('\n');
        }

        in_flight.get();

        // 末尾不足一块：填零至 disk_align 倍数，写入后用 truncate 恢复真实大小
        if (cur_used > 0) {
            char* base = using_a ? buf_a.get_write() : buf_b.get_write();
            const size_t aligned = (cur_used + disk_align - 1) / disk_align * disk_align;
            std::memset(base + cur_used, 0, aligned - cur_used);
            const uint64_t real_total = file_offset + cur_used;
            f.dma_write(file_offset, base, aligned).get();
            f.truncate(real_total).get();
        }

        f.flush().get();
        f.close().get();
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
