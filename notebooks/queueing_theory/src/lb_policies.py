import random

import numpy as np


def queue_size(resource):
    return resource.count + len(resource.queue)


def random_lb(request_num, workers):
    return random.randint(0, len(workers) - 1)


def rr_lb(request_num, workers):
    return request_num % len(workers)


def choice_two_lb(request_num, workers):
    r1, r2 = np.random.choice(range(len(workers)), 2, replace=False)
    r1 = random_lb(request_num, workers)
    r2 = random_lb(request_num, workers)
    if queue_size(workers[r1]) < queue_size(workers[r2]):
        return r1
    return r2


def _zone(request):
    return "abc"[request % 3]


def choice_n_weighted(n):
    def lb(request_num, workers):
        choices = np.random.choice(range(len(workers)), n, replace=False)
        result = []
        for idx, w in enumerate(choices):
            weight = 1.0
            if _zone(request_num) == workers[w].zone:
                weight *= 1.0
            else:
                weight *= 4.0
            result.append((w, weight * (1 + queue_size(workers[w]))))

        result = sorted(result, key=lambda x: x[1])
        return result[0][0]
    return lb


def choice_two_adjacent_lb(request_num, workers):
    r1 = random_lb(request_num, workers)
    if r1 + 2 >= len(workers):
        r2 = r1 - 1
        r3 = r1 - 2
    else:
        r2 = r1 + 1
        r3 = r1 + 2

    iq = [(queue_size(workers[i]), i) for i in (r1, r2, r3)]
    return (sorted(iq)[0][1])


def shortest_queue_lb(request_num, workers):
    idx = 0
    for i in range(len(workers)):
        if queue_size(workers[i]) < queue_size(workers[idx]):
            idx = i
    return idx
