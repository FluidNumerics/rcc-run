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

# Install rcc-run
RUN mkdir -p /opt/rcc-run/etc
COPY bin /opt/rcc-run/bin
COPY etc /opt/rcc-run/etc

RUN apt-get update -y && \
    apt-get install -y python3-pip && \
    pip3 install pyhcl jsonschema==3.0.2 pyyaml

ENTRYPOINT ["python3","/opt/rcc-run/bin/rcc-run.py"]
