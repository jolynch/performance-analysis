all: build test_baseline test_end test_100m test_10m test_1m test_64k

build:
	gcc benchmark.c -o fsync_bench

test_baseline: build
	echo
	echo "Writing 100 MiB in 4kib blocks, no fdatasync"
	./fsync_bench -b 4096 -f 0
	sync

test_end: build
	echo
	echo "Writing 100 MiB in 4kib blocks, one fdatasync at end"
	./fsync_bench -b 4096
	sync

test_100m: build
	echo
	echo "Writing 100MiB in 4KiB blocks, sync per 100MiB"
	./fsync_bench -b 4096 -f 104857600
	sync

test_10m: build
	echo
	echo "Writing 100MiB in 4KiB blocks, sync per 10MiB"
	./fsync_bench -b 4096 -f 10485760
	sync

test_1m: build
	echo
	echo "Writing 100MiB in 4KiB blocks, sync per 1MiB"
	./fsync_bench -b 4096 -f 1048576
	sync

test_64k: build
	echo
	echo "Writing 100MiB in 4KiB blocks, sync per 64KiB"
	./fsync_bench -b 4096 -f 65536
	sync
