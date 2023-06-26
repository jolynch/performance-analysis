#include <stdlib.h>
#include <fcntl.h>

#include <unistd.h>
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <time.h>

static long size[] = {
    // Never sync
    0,
    // Sync at the end
    -1,
    // Sync every 100MiB
    100 * 1024 * 1024,
    // Sync every 10MiB
    10  * 1024 * 1024,
    // Sync every MiB
    1   * 1024 * 1024,
    // Sync every 512KiB etc ...
           512 * 1024,
           256 * 1024,
           128 * 1024,
            64 * 1024,
            32 * 1024,
            16 * 1024
};

void usage (char *argv[]) {
    fprintf(stderr, "Usage: %s [OPTION] [FILE]...\n", argv[0]);
    fprintf(stderr, "  -b    Write block size (4096)\n");
    fprintf(stderr, "  -t    Target size in bytes (1073741824)\n");
    fprintf(stderr, "  -f    Call fdatasync after this many bytes. 0 syncs at the end of writes and -1 disables (0)\n");
    fprintf(stderr, "  -l    Number of trials to run during benchmark (10)\n");
    fprintf(stderr, "  -r    Run a benchmark doing multiple iterations at various fsync intervals\n");
    exit(EXIT_FAILURE);
}

// Return the milliseconds to run
long long run_iteration(long buf_size, long target_size, long fsync_size) {
    long num_iterations;
    char buf[buf_size];
    struct timespec start;
    struct timespec end;

    num_iterations = target_size / buf_size;
    fprintf(
        stderr,
        "Writing %ld MiB in chunks of %ld for %ld syscalls. Fsync every %ld KiB ...",
        target_size / (1024 * 1024), buf_size, num_iterations, fsync_size / (1024));

    int fd = open("test.bin", O_RDWR | O_CREAT, S_IRUSR | S_IWUSR);
    for (long i = 0; i < buf_size; i++) {
        buf[i] = 'x';
    }

    long written = 0;
    long next_fsync = 0;
    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int i = 0; i < num_iterations; i++) {
        write(fd, buf, buf_size);
        if (fsync_size > 0) {
            written += buf_size;
            if (written > next_fsync) {
                fdatasync(fd);
                next_fsync += fsync_size;
            }
        }
    }
    // Support "sync on close"
    if (fsync_size < 0) {
        fdatasync(fd);
    }

    clock_gettime(CLOCK_MONOTONIC, &end);

    // TODO
    // read time in queue from /sys/block/nvme0n1/stat
    // divide by elapsed time, get avg queue size.
    close(fd);

    long long start_ms = start.tv_sec * 1000 + start.tv_nsec/1000000;
    long long end_ms = end.tv_sec * 1000 + end.tv_nsec/1000000;
    fprintf(stderr, " Done in %lld millis\n", end_ms - start_ms);
    return end_ms - start_ms;
}


int main(int argc, char *argv[]) {
    long buf_size = 4096;
    long target_size = 1024 * 1024 * 1024;
    long fsync_size = -1;
    int  trials = 20;
    int  bench = 0;

    int opt;
    long result;

    while ((opt = getopt(argc, argv, "b:t:f:l:r")) != -1 ) {
        switch (opt) {
        case 'b':
            buf_size = atol(optarg);
            break;
        case 't':
            target_size = atol(optarg);
            break;
        case 'f':
            fsync_size = atol(optarg);
            break;
        case 'l':
            trials = atoi(optarg);
            break;
        case 'r':
            bench = 1;
            break;
        default:
            usage(argv);
            exit(EXIT_FAILURE);
        }
    }
    if (buf_size == 0) buf_size = 4096;
    if (bench == 1) {
        fprintf(stderr, "Running %d trials writing %ldKiB of data\n", trials, target_size / (1024));
        printf("{\n");
        for (int i = 0; i < 11; i++) {
            fsync_size = size[i];
            printf("  %ld: [", fsync_size);
            for (int j = 0; j < trials; j++) {
                result = run_iteration(buf_size, target_size, fsync_size);
                if (j + 1 < trials) printf("%ld, ", result);
                else printf("%ld", result);
            }
            printf("],\n");
        }
        printf("}\n");
    } else {
        result = run_iteration(buf_size, target_size, fsync_size);
        fprintf(stdout, "%ld -> %ld millis\n", fsync_size, result);
    }
}

