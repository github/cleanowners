#checkov:skip=CKV_DOCKER_2
#checkov:skip=CKV_DOCKER_3
FROM python:3.13.7-slim@sha256:8220ccec22e88cddd9a541cacd1bf48423bda8cdeb1015249e4b298edf86cdc7
LABEL org.opencontainers.image.source https://github.com/github/cleanowners

WORKDIR /action/workspace
COPY requirements.txt *.py /action/workspace/

RUN python3 -m pip install --no-cache-dir -r requirements.txt \
    && apt-get -y update \
    && apt-get -y install --no-install-recommends git=1:2.47.2-0.2 \
    && rm -rf /var/lib/apt/lists/*

CMD ["/action/workspace/cleanowners.py"]
ENTRYPOINT ["python3", "-u"]
