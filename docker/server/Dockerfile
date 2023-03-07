FROM kumatea/bot:latest

# Create conda environment
RUN set -ex && \
    wget https://github.com/KumaTea/docker/tarball/master -O /tmp/kuma-docker.tar.gz && \
    mkdir -p /tmp/docker && \
    tar -xzf /tmp/kuma-docker.tar.gz -C /tmp/docker --strip-components 1 && \
    bash /tmp/docker/scripts/install-packages.sh "flask pillow gunicorn transformers pytorch cpuonly -c pytorch" "" && \
    rm -rf /tmp/docker && \
    rm /tmp/kuma-docker.tar.gz

# Set entrypoint
ENTRYPOINT ["/bin/bash", "/home/kuma/bots/KumaGPT/docker/server/run-docker.sh"]

# Command
# docker run -d --name cap -v /home/kuma/bots/KumaGPT:/home/kuma/bots/KumaGPT -p 14500:14500 --restart unless-stopped kumatea/cap:latest
