#!/bin/bash
SERVICE="benchmark"

echo "Running: ab -g latency.dat $@"
ab -g latency.dat "$@"
if [ $? -eq 0 ]; then
    python latency_heatmap/latency_heatmap.py --num-values 10 latency.dat $SERVICE
fi
echo "Result is at ${SERVICE}.png"
rm -f latency.dat
