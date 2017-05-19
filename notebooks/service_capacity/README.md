Service Capacity
================

This notebook helps you model how prepared your service is for load. You can
specify how many workers you're running, how much QPS you expect, and what
your average latency is and the model will answer two questions:

1. Is this enough capacity (and how many more workers or accept threads do you need)
2. Whether you will run out of capacity when a downstream service starts
   timing out
