###############################
Customize the Test Cluster
###############################
When you use RCC-Run, an ephemeral `RCC cluster <https://research-computing-cluster.readthedocs.io/en/latest/>`_ is created with `Terraform <https://terraform.io>`_ to run Slurm batch jobs on your behalf. The RCC cluster is defined using the `rcc-tf module <https://github.com/FluidNumerics/rcc-tf>`_. The default variable concretizations are provided in `rcc-run/etc/rcc-ephemeral/default/fluid.auto.tfvars <https://github.com/FluidNumerics/rcc-run/blob/main/etc/rcc-ephemeral/default/fluid.auto.tfvars>`_. This default configuration provides you with a n1-standard-16 controller with a 1TB pd-ssd disk and a single compute partition, consisting of 5x c2-standard-8 instances. 

The rcc-run builder provides a mechanism to customize the cluster so that you can define compute partitions that meet your testing needs. You are able to add `instances with GPUs <https://cloud.google.com/compute/docs/gpus>`_, specify partitions for a heterogeneous cluster (see `machine types available on Google Cloud <https://cloud.google.com/compute/docs/machine-types>`_), specify the zone to deploy to, change the controller size, shape, and disk properties, and even add a Lustre file system.


*****************
Getting Started
*****************
To customize the cluster, you can add a tfvars definition file that is similar to the `rcc-run/etc/rcc-ephemeral/default/fluid.auto.tfvars <https://github.com/FluidNumerics/rcc-run/blob/main/etc/rcc-ephemeral/default/fluid.auto.tfvars>`_. For reference, the `rcc-run/etc/rcc-ephemeral/io.tf <https://github.com/FluidNumerics/rcc-run/blob/main/etc/rcc-ephemeral/io.tf>`_ file defines all of the variables available for concretizing a :code:`rcc-ephemeral` cluster. 

It is recommended that you start by creating a file in your repository called :code:`rcc.auto.tfvars` with the following contents

.. code-block:: yaml 

  cluster_name = "<name>"
  project = "<project>"
  zone = "<zone>"
  
  controller_image = "<image>"
  disable_controller_public_ips = false
  
  login_node_count = 0
  
  suspend_time = 2
  
  
  compute_node_scopes          = [
    "https://www.googleapis.com/auth/cloud-platform"
  ]
  partitions = [
    { name                 = "c2-standard-8"
      machine_type         = "c2-standard-8"
      image                = "<image>"
      image_hyperthreads   = true
      static_node_count    = 0
      max_node_count       = 5
      zone                 = "<zone>"
      compute_disk_type    = "pd-standard"
      compute_disk_size_gb = 50
      compute_labels       = {}
      cpu_platform         = null
      gpu_count            = 0
      gpu_type             = null
      gvnic                = false
      network_storage      = []
      preemptible_bursting = false
      vpc_subnet           = null
      exclusive            = false
      enable_placement     = false
      regional_capacity    = false
      regional_policy      = null
      instance_template    = null
    },
  ]
  
  create_filestore = false
  create_lustre = false


You'll notice that their are a few template variables in this example that are demarked by :code:`<>`. The rcc-run build step is able to substitute values for these variables at build-time based on options provided to the command lined interface. The example above provides a good starting point with some of the necessary template variables in place. It is not recommended to remove the template variables for :code:`<name>`, :code:`<project>`, :code:`<zone>`, or :code:`<image>`.


For your reference, template variables for :code:`rcc-ephemeral` clusters that are substituted at run-time are given in the table below.

====================  =======================  ===============================================
Template Variable     Value/CLI Option         Description
====================  =======================  ===============================================
<name>                 frun-{build-id}[0:7]    Name of the ephemeral cluster
<project>              --project               Google Cloud Project ID
<zone>                 --zone                  Google Cloud zone
<image>                --gce-image             Google Compute Engine VM Image self-link
<build_id>             --build-id              Google Cloud Build build ID
<vpc_subnet>           --vpc-subnet            Google Cloud VPC Subnetwork
<service_account>      --service-account       Google Cloud Service Account email address
====================  =======================  ===============================================


**********************
Customize Partitions
**********************
Partitions are used to define the type of compute nodes available to you for testing. Each partition consists of a homogeneous pool of machines. While each partition has 22 variables to concretely define it, we'll cover a few of the options here to help you make informed decisions when defining partitions for testing.

name
=====
The partition name is used to identify a homogeneous group of compute nodes. When writing your RCC Run CI File, you will set the :code:`partition` field to one of the partition names set in your :code:`tfvars` file.

machine_type
=============
The machine type refers to a `Google Compute Engine machine type <https://cloud.google.com/compute/docs/machine-types>`_. If you define multiple partitions with differing machine types, this gives you the ability to see how your code's performance varies across different hardware

max_node_count
===============
This is the maximum number of nodes that can be created in this partition. When tests are run, the cluster will automatically manage provisioning compute nodes to run benchmarks and tear them down upon completion. Keep in mind that you need to ensure that you have `sufficient Quota <https://cloud.google.com/compute/quotas>`_ for the machine type, gpus, and disks in the region that your cluster is deployed to.

image
=======
The :code:`image` expects a self-link to a VM image for the cluster. It is recommended that you leave this field set to the template variable :code:`"<image>"` so that rcc-run can set this field for you. The default image that RCC uses is :code:`projects/research-computing-cloud/global/images/family/rcc-run-foss`, which includes Singularity and OpenMPI 4.0.5.

gpu_type / gpu_count
========================
The :code:`gpu_type` field is used to set the type of GPU to attach to each compute node in the partition. Possible values are

* nvidia-tesla-k80
* nvidia-tesla-p100
* nvidia-tesla-v100
* nvidia-tesla-p4
* nvidia-tesla-t4
* nvidia-tesla-a100 (`A2 instances only <https://cloud.google.com/compute/docs/accelerator-optimized-machines>`_) 


The :code:`gpu_count` field is used to set the number of GPUs per machine in the partition. For most GPUs, you can set this to 0, 1, 2, 4, or 8. Currently, GPUs must be used with an *n1* machine type on Google Cloud (`except for the A100 GPUs <https://cloud.google.com/compute/docs/accelerator-optimized-machines>`_). 
Keep in mind that each GPU type is available in `certain zones <https://cloud.google.com/compute/docs/gpus/gpu-regions-zones>`_ and that there are `restrictions on the ratio of vCPU to GPU <https://cloud.google.com/compute/docs/gpus>`_.


