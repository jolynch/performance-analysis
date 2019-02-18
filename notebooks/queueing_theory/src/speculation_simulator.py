import random
from collections import namedtuple

import numpy as np
import simpy

LatencyDatum = namedtuple(
    'LatencyDatum',
    ('t_queued', 't_processing', 't_total')
)


class SpeculatingRequestExecutor(object):
    """ Simulates a M/G/k process common in request processing (computing) but
    with always on speculation to another host

    :param worker_desc: A tuple of (count, capacity) to construct workers with
    :param local_balancer: A function which takes the current request number
        and the list of workers and returns the index of the worker to
        send the next request to
    :param latency_fn: A function which takes the curent request number and the
        worker that was assigned by the load balancer and returns the number of
        milliseconds a request took to process
    :param number_of_requests: The number of requests to run through the
        simulator
    :param request_per_s: The rate of requests per second.
    """

    def __init__(
            self, worker_desc, load_balancer, latency_fn,
            number_of_requests, request_per_s):
        self.worker_desc = worker_desc
        self.load_balancer = load_balancer
        self.latency_fn = latency_fn
        self.number_of_requests = int(number_of_requests)
        self.request_interval_ms = 1. / (request_per_s / 1000.)
        self.received_first = {'1': 0, '2': 0}
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
            workers = []
            for j in range(2):
                idx = self.load_balancer(i, self.workers)
                workers.append(self.workers[idx])
            response = self.process_request(
                i, workers[0], workers[1],
            )
            self.env.process(response)
            # Exponential inter-arrival times == Poisson
            arrival_interval = random.expovariate(
                1.0 / self.request_interval_ms
            )
            yield self.env.timeout(arrival_interval)

    def process_request(self, request_id, worker1, worker2):
        """ Request arrives, possibly queues, and then processes"""
        t_arrive = self.env.now

        req1 = worker1.request()
        req2 = worker2.request()

        try:
            result = yield req1 | req2

            if req1 in result:
                self.received_first['1'] += 1
                req2.cancel()
                req2.resource.release(req2)
            else:
                self.received_first['2'] += 1
                req1.cancel()
                req1.resource.release(req1)

            t_start = self.env.now
            t_queued = t_start - t_arrive

            # Let the operation take w.e. amount of time the latency
            # function tells us to
            yield self.env.timeout(self.latency_fn(request_id))

            t_done = self.env.now
            t_processing = t_done - t_start
            t_total_response = t_done - t_arrive
            self.data.append(LatencyDatum(
                t_queued, t_processing, t_total_response))
        finally:
            worker1.release(req1)
            worker2.release(req2)


def run_speculation(
        worker_desc, load_balancer, num_requests, request_per_s, latency_fn):
    simulator = SpeculatingRequestExecutor(
        worker_desc, load_balancer, latency_fn,
        num_requests, request_per_s
    )
    simulator.simulate()
    return simulator.data, simulator.received_first
