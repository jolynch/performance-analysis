import random

import numpy as np
import simpy


class RequestSimulator(object):
    """ Simulates a M/G/k process common in request processing (computing)

    :param worker_desc: A tuple of (count, capacity) to construct workers with
    :param local_balancer: A function which takes the current request number
                           and the list of workers and returns the index of the
                           worker to send the next request to
    :param latency_fn: A parameterless function which returns the number of
                       milliseconds a request took to process
    :param number_of_requests: The number of requests to run through the
                               simulator
    :param request_per_s: The rate of requests per second.
    """

    def __init__(
            self, worker_desc, load_balancer, latency_fn,
            number_of_requests, request_per_s
    ):
        self.worker_desc = worker_desc
        self.load_balancer = load_balancer
        self.latency_fn = latency_fn
        self.number_of_requests = int(number_of_requests)
        self.request_interval_ms = 1. / (request_per_s / 1000.)
        self.data = []

    def simulate(self):
        # Setup and start the simulation
        random.seed(1)
        np.random.seed(1)

        self.env = simpy.Environment()
        count, cap = self.worker_desc
        self.workers = [
            simpy.Resource(self.env, capacity=cap) for i in range(count)
        ]
        self.env.process(self.generate_requests())
        self.env.run()

    def generate_requests(self):
        for i in range(self.number_of_requests):
            idx = self.load_balancer(i, self.workers)
            worker = self.workers[idx]
            response = self.process_request(
                'Request%02d' % i, worker,
            )
            self.env.process(response)
            # Exponential inter-arrival times == Poisson
            arrival_interval = random.expovariate(
                1.0 / self.request_interval_ms
            )
            yield self.env.timeout(arrival_interval)

    def process_request(self, name, worker):
        """ Request arrives, possibly queues, and then processes"""
        t_arrive = self.env.now

        with worker.request() as req:
            yield req

            t_start = self.env.now
            t_queued = t_start - t_arrive

            # Let the operation take w.e. amount of time the latency
            # function tells us to
            yield self.env.timeout(self.latency_fn())

            t_done = self.env.now
            t_processing = t_done - t_start
            t_total_response = t_done - t_arrive

            datum = (t_queued, t_processing, t_total_response)
            self.data.append(datum)


def queue_size(resource):
    return resource.count + len(resource.queue)


def random_lb(request_num, workers):
    return random.randint(0, len(workers) - 1)


def rr_lb(request_num, workers):
    return request_num % len(workers)


def choice_two_lb(request_num, workers):
    r1 = random_lb(request_num, workers)
    r2 = random_lb(request_num, workers)
    if queue_size(workers[r1]) < queue_size(workers[r2]):
        return r1
    return r2


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


lb_algos = {
    'choice_two': choice_two_lb,
    'random': random_lb,
    'roundrobin': rr_lb,
    'JSQ': shortest_queue_lb,
}


def pareto(mean, shape):
    # mean = scale * shape / (shape - 1)
    # solve for scale given mean and shape (aka skew)
    scale = mean - mean / shape
    return lambda: ((np.random.pareto(shape) + 1) * scale)


def expon(mean):
    return lambda: random.expovariate(1.0 / mean)


# Simulate the various choices
NUM_REQUESTS = 50000
QPS = 20000
AVG_RESPONSE_MS = 0.4
SERVERS = 10


def run_simulation(
        worker_desc, load_balancer, num_requests, request_per_s, latency_fn
):
    simulator = RequestSimulator(
        worker_desc, load_balancer, latency_fn,
        num_requests, request_per_s
    )
    simulator.simulate()
    return simulator.data


# M/G/k queue mean slowdown
for i in run_simulation(
        (1, SERVERS), rr_lb, NUM_REQUESTS, QPS, pareto(AVG_RESPONSE_MS, 2)):
    print(i[2] / i[1])
