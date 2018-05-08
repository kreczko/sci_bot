FROM python:alpine3.6

LABEL maintainer="Luke Kreczko <kreczko@cern.ch>"

ARG LIBRESSL_VERSION=2.6
ARG LIBRDKAFKA_VERSION=0.11.1-r1

RUN apk update && \
    apk add --no-cache \
            alpine-sdk \
            bash \
            build-base \
            coreutils \
            cyrus-sasl-dev \
            krb5 \
            libffi-dev \
            libsasl \
            openssl \
            openssl-dev \
            zlib-dev

RUN apk add --no-cache \
            libressl${LIBRESSL_VERSION}-libcrypto \
            libressl${LIBRESSL_VERSION}-libssl \
             --repository http://nl.alpinelinux.org/alpine/edge/main && \
    apk add --no-cache \
            librdkafka-dev=${LIBRDKAFKA_VERSION} \
            librdkafka=${LIBRDKAFKA_VERSION} \
            --repository http://nl.alpinelinux.org/alpine/edge/community


# ci bot bits
COPY docker/cdw /usr/local/bin/cdw
COPY docker/bashrc /root/.bashrc

# Add our code
ADD . /app/user
WORKDIR /app/user
# install app as development image
RUN python setup.py develop

# Run the image as a non-root user
RUN adduser -D myuser
RUN chown -R myuser /app/user
USER myuser
