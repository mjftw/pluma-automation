FROM ubuntu:20.04

# Add UTF-8 locale
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update \
 && apt-get dist-upgrade -y \
 && apt-get install -y locales && locale-gen en_US.UTF-8 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Copy pluma
COPY ./ /root/pluma

# Install pluma
RUN /root/pluma/install.sh -n \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir /etc/pluma \
 && cp /root/pluma/pluma.yml.sample /etc/pluma/pluma.yml \
 && cp /root/pluma/pluma-target.yml.sample /etc/pluma/pluma-target.yml

CMD ["python3", "-m", "pluma", "-c", "/etc/pluma/pluma.yml", "-t", "/etc/pluma/pluma-target.yml"]