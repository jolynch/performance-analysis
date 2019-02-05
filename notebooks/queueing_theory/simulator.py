import random

import numpy as np
import simpy


RANDOM_SEED = 42
NUM_REQUESTS = 20000
# query per millisecon
# Queries per second
QPS = 1000
QPMS = QPS / 1000
INTERVAL_QUERY_MS = 1 / QPMS
AVG_RESPONSE_MS = 1
SERVERS = 3


def queue_size(resource):
    return resource.count + len(resource.queue)


def mmk(env, number, interval, counters):
    """Source generates customers randomly"""
    for i in range(number):
        # Random lb
        #idx = random.randint(0, len(counters)-1)
        # Round robin
        #idx = i % len(counters)
        # Pick two
        r1 = random.randint(0, len(counters)-1)
        r2 = random.randint(0, len(counters)-1)
        if queue_size(counters[r1]) < queue_size(counters[r2]):
            idx = r1
        else:
            idx = r2
        # least con
        # idx = sorted([(queue_size(k), k) for k in counters], key=lambda x :
        #    x[0])[0]
        #idx = counters.index(idx[1])

        c = process_web_request(env, 'Request%02d' %
                                i, counters[idx], processing_time=AVG_RESPONSE_MS)
        env.process(c)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)


def source(env, number, interval, counter):
    """Source generates customers randomly"""
    for i in range(number):
        c = process_web_request(env, 'Request%02d' %
                                i, counter, processing_time=AVG_RESPONSE_MS)
        env.process(c)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)


def process_web_request(env, name, counter, processing_time):
    """Customer arrives, is served and leaves."""
    arrive = env.now

    with counter.request() as req:
        results = yield req

        start = env.now
        wait = start - arrive

        # We got to the counter
        #print('%7.4f %s: queued for %6.3f' % (env.now, name, wait))
        # print(wait)

        tib = (np.random.pareto(2, 1) + processing_time)[0]
        yield env.timeout(tib)

        done = env.now - arrive
        #print('%7.4f %s: done after %6.3f' % (env.now, name, done))
        print(done)
        #print(done / (env.now - start))



# Setup and start the simulation
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
env = simpy.Environment()

# Start processes and run
counter = simpy.Resource(env, capacity=SERVERS)
counters = [simpy.Resource(env, capacity=1) for i in range(SERVERS)]
env.process(mmk(env, NUM_REQUESTS, INTERVAL_QUERY_MS, counters))
#env.process(source(env, NUM_REQUESTS, INTERVAL_QUERY_MS, counter))
env.run()
