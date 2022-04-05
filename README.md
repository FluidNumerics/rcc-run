# RCC Run
Copyright 2021 Fluid Numerics LLC


RCC Run is a tool for benchmarking high performance computing (HPC) and research computing (RC) applications on ephemeral resources on Google Cloud. 

The motivation for developing rcc-run is to support continuous integration and continuous benchmarking (CI/CB) of HPC and RC applications at scale on Google Cloud.  By using rcc-run as a build step with Google Cloud Build, developers can automate testing and benchmarking on GPU accelerated and multi-VM platforms hosted on Google Cloud. Information about the each test, including the system architecture, software version (git sha), build id, and application runtime are recorded and can be saved to Big Query. This allows developers to create an auditable trail of data that comments on the performance of an application over time and accross various hardware.

## Support
Issues, feature requests, and general support requests can be submitted through [Fluid Numerics' Community Support channel](https://fluid-run.readthedocs.io/en/latest/Support/support.html)


## Documentation
Documentation is available at https://fluid-run.readthedocs.io/en/latest/


## Projects using rcc-run

*Feel free to add your project using a pull request*


* [SELF](https://github.com/FluidNumerics/SELF)



