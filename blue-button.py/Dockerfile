FROM python:3.9.6-alpine3.14

ARG CERT_PATH_BUILD_ARG="./conf/certs"

RUN apk update && \
    apk add ca-certificates && \
    apk add --no-cache build-base \
        openssl \
        python3-dev

# install certificates
# copy certificates and keys
WORKDIR /usr/local/share/ca-certificates/
COPY $CERT_PATH_BUILD_ARG/*.pem ./
COPY $CERT_PATH_BUILD_ARG/*.key ./
RUN chmod 644 *.pem *.key && \
    update-ca-certificates && \
    addgroup -S lfh && \
    adduser -S lfh -G lfh -h /home/lfh

WORKDIR /home/lfh/bluebutton
RUN mkdir config && \
    chown -R lfh:lfh /home/lfh/bluebutton

# copy config files
COPY --chown=lfh:lfh Pipfile.lock logging.yaml ./

# configure application
COPY --chown=lfh:lfh ./bluebutton ./bluebutton
USER lfh
RUN python -m pip install --user --upgrade pip pipenv && \
    /home/lfh/.local/bin/pipenv sync

EXPOSE 5200
WORKDIR /home/lfh/bluebutton
ENV PYTHONPATH="."
CMD ["/home/lfh/.local/bin/pipenv", "run", "python", "bluebutton/main.py"]
