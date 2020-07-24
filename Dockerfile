FROM ubuntu:18.04

# Add UTF-8 locale
RUN apt-get update && apt-get install -y locales && locale-gen en_US.UTF-8

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Copy farm core
COPY ./ /root/farm-core

# Install farm core
RUN /root/farm-core/install.sh -n

CMD ["/root/farm-core/pluma.py", "-c", "/etc/pluma/pluma.yml", "-t", "/etc/pluma/pluma-target.yml"]