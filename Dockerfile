# builder image
FROM python:3-slim AS builder
RUN mkdir /src
COPY . /src/
RUN python -m venv /opt/venv
RUN . /opt/venv/bin/activate \
  && pip install \
    --no-cache-dir \
    --upgrade \
      pip setuptools wheel \
  && apt-get update -y \
  && apt install -y \
    git build-essential \
  && cd /src \
  && pip install --no-cache-dir .

# main image
FROM python:3-alpine AS app
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENTRYPOINT ["/opt/venv/bin/linode_dyndns"]
