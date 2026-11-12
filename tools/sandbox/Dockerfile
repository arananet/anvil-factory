# Station sandbox image for runtime.sandbox (kind docker) in anvil.yaml.
# Build: docker build -t anvil-station:latest tools/sandbox
# The container gets the project tree, the model gateway variables and
# nothing else of the host. See docs/OPERATIONS.md, Station sandbox.
FROM node:22-bookworm-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 git ca-certificates \
 && rm -rf /var/lib/apt/lists/*
RUN npm install -g @anthropic-ai/claude-code
ENV HOME=/tmp
