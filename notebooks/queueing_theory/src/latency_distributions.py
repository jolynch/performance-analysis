import random

import numpy as np


def pareto(mean, shape):
    # mean = scale * shape / (shape - 1)
    # solve for scale given mean and shape (aka skew)
    scale = mean - mean / shape

    def latency(request):
        return ((np.random.pareto(shape) + 1) * scale)
    return latency


def expon(mean):
    def latency(request):
        return random.expovariate(1.0 / mean)
    return latency
