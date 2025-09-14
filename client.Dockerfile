FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir httpx requests

# Copy the client scripts (these will be overridden by the volume mount)
COPY client/api_client.py /app/api_client.py
COPY client/test_api.py /app/test_api.py
RUN chmod +x /app/api_client.py /app/test_api.py

# Create a wrapper script
RUN echo '#!/bin/bash' > /app/entrypoint.sh && \
    echo 'if [ "$1" = "tail" ]; then' >> /app/entrypoint.sh && \
    echo '  exec tail -f /dev/null' >> /app/entrypoint.sh && \
    echo 'elif [ "$1" = "test" ]; then' >> /app/entrypoint.sh && \
    echo '  exec python /app/client/test_api.py "${@:2}"' >> /app/entrypoint.sh && \
    echo 'else' >> /app/entrypoint.sh && \
    echo '  exec python /app/api_client.py "$@"' >> /app/entrypoint.sh && \
    echo 'fi' >> /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
