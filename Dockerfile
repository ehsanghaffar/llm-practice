# syntax = docker/dockerfile:1.4

FROM tiangolo/uvicorn-gunicorn:python3.11-slim AS builder

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
# RUN pip install -r requirements.txt

COPY . .

FROM builder as dev-envs

RUN <<EOF
apt-get update
apt-get install -y --no-install-recommends git
python -m nltk.downloader punkt
EOF

# RUN <<EOF
# useradd -s /bin/bash -m vscode
# groupadd docker
# usermod -aG docker vscode
# EOF
# # install Docker tools (cli, buildx, compose)
# COPY --from=gloursdocker/docker / /