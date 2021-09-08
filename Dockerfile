FROM gcr.io/cloud-builders/gcloud AS builder

# Install terraform
RUN apt-get update -y && \ 
    apt-get install -y wget unzip &&\
    wget https://releases.hashicorp.com/terraform/1.0.3/terraform_1.0.3_linux_amd64.zip --directory-prefix=/tmp &&\
    cd /tmp/ &&\
    unzip terraform_1.0.3_linux_amd64.zip &&\
    mv terraform /usr/local/bin/

FROM gcr.io/cloud-builders/gcloud

# Install terraform
COPY --from=builder /usr/local/bin/terraform /usr/local/bin/terraform

# Install fluid-run
RUN mkdir -p /opt/fluid-run/etc
COPY bin /opt/fluid-run/bin
COPY etc /opt/fluid-run/etc

RUN apt-get update -y && \
    apt-get install -y python3-pip && \
    pip3 install pyhcl

ENTRYPOINT ["python3","/opt/fluid-run/bin/fluid-run.py"]
