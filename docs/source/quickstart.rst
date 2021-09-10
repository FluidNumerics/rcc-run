

Quickstart
======================================

Fluid Run is used to create ephemeral compute resources for testing HPC applications and to record information about the test for later analysis.
This quickstart guide will introduce you to the necessary ingredients for configuring application tests with fluid-run.

.. _gcpsetup:

Google Cloud Project Setup
---------------------------
To complete this tutorial, you will need to have an active project on Google Cloud. 
Sign up and create your first project by visiting https://console.cloud.google.com

Once your project is ready, `open Cloud Shell <https://shell.cloud.google.com/?show=terminal>`_

You will need to activate the following Google Cloud APIs

* Compute Engine
* Cloud Build
* Big Query
* Identity & Access Management (IAM) 

.. code-block:: shell

gcloud config set project *PROJECT-ID*
gcloud services enable compute.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable iam.googleapis.com
gcloud services enable cloudbuild.googleapis.com



.. _createcicbdataset:

Create the CI/CB Dataset
---------------------------


.. _createdockerimage:

Create a fluid-run Docker image
--------------------------------

.. _cloudbuilddemo:

Cloud Build demo
-----------------
