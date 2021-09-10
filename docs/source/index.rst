.. fluid-run documentation master file, created by
   sphinx-quickstart on Wed Sep  8 15:35:38 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Fluid Run
======================================
Fluid Run is a tool for running high performance computing (HPC) and research computing (RC) applications on ephemeral resources on Google Cloud.
The motivation for developing fluid-run is to support continuous integration and continuous benchmarking (CI/CB) of HPC and RC applications at scale on Google Cloud. 
By using fluid-run as a build step with Google Cloud Build, developers can automate running tests on GPU accelerated and multi-VM platforms hosted on Google Cloud. 
Information about the each test, including the system architecture, software version (git sha), build id, and application runtime are recorded and can be saved to Big Query.
This allows developers to create an auditable trail of data that comments on the performance of an application over time and accross various hardware.




.. toctree::

   QuickStart/index
   Reference/index
   Support/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`