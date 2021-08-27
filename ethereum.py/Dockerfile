FROM python:3.9.6-alpine3.14

ARG ETHEREUM_CERT_PATH_BUILD_ARG="./conf/certs"
ARG ETHEREUM_CONFIG_PATH_BUILD_ARG="./conf/config"

RUN apk update && \
    apk add ca-certificates && \
    apk add --no-cache build-base \
        openssl \
        python3-dev

# install certificates
# copy certificates and keys
WORKDIR /usr/local/share/ca-certificates/
COPY $ETHEREUM_CERT_PATH_BUILD_ARG/*.pem ./
COPY $ETHEREUM_CERT_PATH_BUILD_ARG/*.key ./
RUN chmod 644 *.pem *.key && \
    update-ca-certificates && \
    addgroup -S lfh && \
    adduser -S lfh -G lfh -h /home/lfh

WORKDIR /home/lfh/ethereum
RUN mkdir config && \
    chown -R lfh:lfh /home/lfh/ethereum

# copy config files
COPY --chown=lfh:lfh $ETHEREUM_CONFIG_PATH_BUILD_ARG/nats-server.nk ./config/
COPY --chown=lfh:lfh $ETHEREUM_CONFIG_PATH_BUILD_ARG/EligibilityCheck.json ./config/
COPY --chown=lfh:lfh Pipfile.lock logging.yaml ./

# configure application
COPY --chown=lfh:lfh ./ethereum ./ethereum
USER lfh
RUN python -m pip install --user --upgrade pip pipenv && \
    /home/lfh/.local/bin/pipenv sync

EXPOSE 5001
WORKDIR /home/lfh/ethereum
ENV PYTHONPATH="."
CMD ["/home/lfh/.local/bin/pipenv", "run", "python", "ethereum/main.py"]
