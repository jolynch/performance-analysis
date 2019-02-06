Queueing Analysis
=================

This notebook explores different queueing models using
[SimPy](https://simpy.readthedocs.io/en/latest/) as many of these algorithms do
not have closed for solutions. In particular we show that a single queue is
dominant to multiple queues, and given multiple queues you should strive as
much as possible to join the shortest queue possible.

The following queueuing systems are evaluated:
* M/G/k queueing: A single queue that feeds into k workers
* Round robin: Iterating the workers in a list and sending to one after the
  other
* Join shorted queue: Join the worker with the smallest queue.
* Random: Choose a worker at random
* Choice of two: Choose two workers at random and then join the shorter queue

The arrivals are memoryless either way (exponential inter-arrival delay) and
the processing time is modeled with a [pareto](https://en.wikipedia.org/wiki/Pareto_distribution) distribution.

TODO: mean slowdown analysis.
