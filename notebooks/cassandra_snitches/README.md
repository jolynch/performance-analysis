Cassandra Latency And Snitching Evaluation
==========================================

This notebook explores a realistic latency model for Cassandra (multi-mode)
that takes into account common sources of latency.

The goal is to evaluate different load balancing and snitching algorithms for
[CASSANDRA-14459](https://issues.apache.org/jira/browse/CASSANDRA-14459)
and [CASSANDRA-14817](https://issues.apache.org/jira/browse/CASSANDRA-14817).

