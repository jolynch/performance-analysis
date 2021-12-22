import random

import numpy as np


def zone(request):
    return "abc"[request % 3]


def service(mean, slow, shape, slow_freq, slow_count):
    scale = mean - mean / shape
    scale_slow = slow - slow / shape

    def latency(request, worker):
        base = ((np.random.pareto(shape) + 1) * scale)
        if (zone(request) != worker.zone):
            base += 0.8
        if (request % slow_freq) < slow_count:
            add_l = ((np.random.pareto(shape) + 1) * scale_slow)
        else:
            add_l = 0
        return base + add_l
    return latency


def pareto(mean, shape):
    # mean = scale * shape / (shape - 1)
    # solve for scale given mean and shape (aka skew)
    scale = mean - mean / shape

    def latency(request, worker):
        return ((np.random.pareto(shape) + 1) * scale)
    return latency


def expon(mean):
    def latency(request, worker):
        return random.expovariate(1.0 / mean)
    return latency
