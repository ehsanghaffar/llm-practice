# syntax = docker/dockerfile:1.4

FROM tiangolo/uvicorn-gunicorn:python3.11 AS builder

WORKDIR /app

RUN pip install --upgrade pip

RUN <<EOF
apt-get update
add-apt-repository ppa:ubuntu-toolchain-r/test
apt update
apt install gcc-11 g++-11 -y
update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 60 --slave /usr/bin/g++ g++ /usr/bin/g++-11
EOF

COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
# RUN pip install -r requirements.txt

COPY . .

FROM builder as dev-envs

# RUN <<EOF
# apt-get update
# sudo add-apt-repository ppa:ubuntu-toolchain-r/test
# sudo apt update
# sudo apt install gcc-11 g++-11
# EOF

# RUN <<EOF
# useradd -s /bin/bash -m vscode
# groupadd docker
# usermod -aG docker vscode
# EOF
# # install Docker tools (cli, buildx, compose)
# COPY --from=gloursdocker/docker / /