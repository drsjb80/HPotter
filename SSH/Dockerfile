FROM debian:bookworm-slim
# Install only the system packages your application actually needs
RUN apt-get update && apt-get install -y curl procps && rm -rf /var/lib/apt/lists/*
CMD ["sleep", "infinity"]
