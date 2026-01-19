#!/bin/bash
# run_in_docker.sh - Run pipeline commands inside tina-devtools container
#
# Usage:
#   ./run_in_docker.sh validate    # Check all connections
#   ./run_in_docker.sh pipeline    # Run full pipeline
#   ./run_in_docker.sh shell       # Open interactive shell

CONTAINER="tina-devtools"
WORKDIR="/workspace/tina-data-engineer/workspace/data_pipeline"

case "$1" in
    validate)
        echo "🔍 Running validation..."
        docker exec -w $WORKDIR $CONTAINER python3 validate.py
        ;;
    pipeline)
        echo "🚀 Running pipeline..."
        docker exec -w $WORKDIR $CONTAINER python3 pipeline.py
        ;;
    shell)
        echo "🐚 Opening shell in container..."
        docker exec -it -w $WORKDIR $CONTAINER bash
        ;;
    *)
        echo "Usage: $0 {validate|pipeline|shell}"
        echo ""
        echo "Commands:"
        echo "  validate  - Check all connections (DB, MinIO, API)"
        echo "  pipeline  - Run the full ETL pipeline"
        echo "  shell     - Open bash shell in container"
        exit 1
        ;;
esac
