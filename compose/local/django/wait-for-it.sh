#!/bin/bash
# Wait for a service to be ready

INITIAL_ARG="$1"

if [[ -z "$INITIAL_ARG" ]]; then
    echo "Error: you need to provide a host and port to test."
    echo "Usage: $0 host:port [-t timeout] [-- command args]"
    exit 1
fi

# Handle host:port format
if [[ "$INITIAL_ARG" == *":"* ]]; then
    HOST="${INITIAL_ARG%:*}"
    PORT="${INITIAL_ARG#*:}"
else
    HOST="$INITIAL_ARG"
    PORT="$2"
    shift 1
fi

TIMEOUT="${3:-30}"

# Parse additional arguments
shift 1
if [[ "$#" -gt 0 && "$1" == "-t" ]]; then
    TIMEOUT="$2"
    shift 2
fi

# Skip -- if present
if [[ "$#" -gt 0 && "$1" == "--" ]]; then
    shift 1
fi

echo "Waiting for $HOST:$PORT (timeout: ${TIMEOUT}s)" >&2

start=$(date +%s)
while true; do
    if timeout 1 bash -c "cat </dev/null >/dev/tcp/$HOST/$PORT" 2>/dev/null; then
        echo "$HOST:$PORT is available" >&2
        break
    fi
    
    elapsed=$(($(date +%s) - start))
    if [[ $elapsed -ge $TIMEOUT ]]; then
        echo "Timeout waiting for $HOST:$PORT" >&2
        exit 1
    fi
    
    sleep 1
done

# Execute command if provided
if [[ $# -gt 0 ]]; then
    exec "$@"
fi

