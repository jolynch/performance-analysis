import random

import numpy as np
import simpy


RANDOM_SEED = 1337


def queue_size(resource):
    return resource.count + len(resource.queue)


class RequestSimulator(object):
    def __init__(
        self, worker_desc, load_balancer,
        number_of_requests, request_per_s, avg_response_time_ms
    ):
        self.worker_desc = worker_desc
        self.load_balancer = load_balancer
        self.number_of_requests = number_of_requests
        self.request_interval_ms = 1. / (request_per_s / 1000.)
        self.avg_response_time_ms = avg_response_time_ms
        self.data = []

    def simulate(self):
        # Setup and start the simulation
        random.seed(RANDOM_SEED)
        np.random.seed(RANDOM_SEED)

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
            response = self.process_web_request(
                'Request%02d' % i, worker,
            )
            self.env.process(response)
            arrival_interval = random.expovariate(
                1.0 / self.request_interval_ms
            )
            yield self.env.timeout(arrival_interval)

    def process_web_request(self, name, worker):
        """ Request arrives, possibly queues, and then processes"""
        t_arrive = self.env.now

        with worker.request() as req:
            yield req

            t_start = self.env.now
            t_queued = t_start - t_arrive

            request_duration = (
                np.random.pareto(2, 1) + self.avg_response_time_ms
            )[0]
            yield self.env.timeout(request_duration)

            t_done = self.env.now
            t_processing = t_done - t_start
            t_total_response = t_done - t_arrive

            datum = (t_queued, t_processing, t_total_response)
            self.data.append(datum)


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


def shortest_queue_lb(request_num, workers):
    idx = 0
    for i in range(len(workers)):
        if queue_size(workers[i]) < queue_size(workers[idx]):
            idx = i
    return idx


def run_simulation(
    worker_desc, load_balancer, num_requests, request_per_s,
    avg_response_ms
):
    simulator = RequestSimulator(
        worker_desc, load_balancer,
        num_requests, request_per_s, avg_response_ms
    )
    simulator.simulate()
    return simulator.data


# M/G/k queue
for i in run_simulation((1, 3), rr_lb, 20000, 2000, 0.4):
    print(i[2])
