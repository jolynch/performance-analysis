Notebooks
=========
In this directory you find a number of [Jupyter Notebooks](http://jupyter.org/)
which allow you to play with and visualize your data. When I'm working on
making nice plots for visualizing data I typically prototype them in Jupyter.

Included Notebooks:
* [Latency Heatmap](latency_heatmap/README.md): A tool for visualizing latencies
  over time as a heatmap. Helps to visualize latency information better than
  percentiles can (e.g. observe periodic latency spikes).
* [Service Capacity](service_capacity/README.md): A tool for calculating
  service capacity given a latency SLO and QPS targets along with downstream
  SLOs. Answers the question "should I scale up or tighten my timeout"
* [Cassandra Availability](cassandra_availability/README.md): Availability
  models of Cassandra under various failure parameters
* [AWS Stateful Instance Analysis](aws_stateful_instance_analysis/README.md):
  Explore how rapidly various EC2 instances can recover from state loss, e.g.
  via EBS or via replicated neighbors.
* [ACCP vs SUN Performance](accp_analysis/README.md) Supporting notebooks for
  my analysis in [ACCP#52](https://github.com/corretto/amazon-corretto-crypto-provider/issues/52).
