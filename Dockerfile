FROM gcr.io/cloud-builders/gcloud

# Install terraform

# Install fluid-cicb
RUN mkdir -p /opt/fluid-cicb/etc

COPY bin /opt/fluid-cicb/bin
COPY tf /opt/fluid-cib/etc/tf
