import random
from collections import namedtuple

import numpy as np
import simpy

LatencyDatum = namedtuple(
    'LatencyDatum',
    ('t_queued', 't_processing', 't_total')
)


class LatencyAwareRequestSimulator(object):
    """ Simulates a M/G/k process common in request processing (computing)

    :param worker_desc: A list of ints of capacities to construct workers with
    :param local_balancer: A function which takes the current request number
        the list of workers and the request time and returns the index of the
        worker to send the next request to
    :param latency_fn: A function which takes the curent request number and
        returns the number of milliseconds a request took to process
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
        self.data = []
        self.requests_per_worker = {}

    def simulate(self):
        # Setup and start the simulation
        random.seed(1)
        np.random.seed(1)

        self.env = simpy.Environment()
        self.workers = []
        idx = 0
        for cap in self.worker_desc:
            self.workers.append(simpy.Resource(self.env, capacity=cap))
            self.requests_per_worker[idx] = 0
            idx += 1
        self.env.process(self.generate_requests())
        self.env.run()

    def generate_requests(self):
        for i in range(self.number_of_requests):
            t_processing = self.latency_fn(i)
            idx = self.load_balancer(i, self.workers, t_processing)
            self.requests_per_worker[idx] += 1
            worker = self.workers[idx]
            response = self.process_request(
                i, worker, t_processing
            )
            self.env.process(response)
            # Exponential inter-arrival times == Poisson
            arrival_interval = random.expovariate(
                1.0 / self.request_interval_ms
            )
            yield self.env.timeout(arrival_interval)

    def process_request(self, request_id, worker, duration):
        """ Request arrives, possibly queues, and then processes"""
        t_arrive = self.env.now

        with worker.request() as req:
            yield req
            t_start = self.env.now
            t_queued = t_start - t_arrive

            yield self.env.timeout(duration)

            t_done = self.env.now
            t_processing = t_done - t_start
            t_total_response = t_done - t_arrive

            datum = LatencyDatum(t_queued, t_processing, t_total_response)
            self.data.append(datum)


def run_simulation(
        worker_desc, load_balancer, num_requests, request_per_s, latency_fn):
    simulator = LatencyAwareRequestSimulator(
        worker_desc, load_balancer, latency_fn,
        num_requests, request_per_s
    )
    simulator.simulate()
    return simulator.data, simulator.requests_per_worker
