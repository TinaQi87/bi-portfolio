#!/bin/bash
# run_in_docker.sh - Run pipeline commands inside tina-devtools container
#
# Usage:
#   ./run_in_docker.sh validate    # Run validation
#   ./run_in_docker.sh pipeline    # Run full pipeline
#   ./run_in_docker.sh shell       # Open interactive shell
#   ./run_in_docker.sh jupyter     # Start Jupyter notebook

CONTAINER="tina-devtools"
WORKDIR="/workspace/tina-data-engineer/workspace/data_pipeline"

# AWS credentials (passed as env vars for boto3)
# These are read from your Mac's AWS config
export AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id 2>/dev/null)
export AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key 2>/dev/null)
export AWS_DEFAULT_REGION=$(aws configure get region 2>/dev/null || echo "ap-southeast-2")

if [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo "⚠️  AWS credentials not found. Run 'aws configure' first."
    exit 1
fi

case "$1" in
    validate)
        echo "🔍 Running validation..."
        docker exec -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION \
            -w $WORKDIR $CONTAINER python3 validate.py
        ;;
    pipeline)
        echo "🚀 Running pipeline..."
        docker exec -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION \
            -w $WORKDIR $CONTAINER python3 pipeline.py
        ;;
    shell)
        echo "🐚 Opening shell in container..."
        docker exec -it -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION \
            -w $WORKDIR $CONTAINER bash
        ;;
    jupyter)
        echo "📓 Jupyter is already running at http://localhost:8888"
        echo "   Open tutorials in: tina-data-engineer/workspace/data_pipeline/"
        ;;
    *)
        echo "Usage: $0 {validate|pipeline|shell|jupyter}"
        echo ""
        echo "Commands:"
        echo "  validate  - Check all connections (DB, S3, API)"
        echo "  pipeline  - Run the full ETL pipeline"
        echo "  shell     - Open bash shell in container"
        echo "  jupyter   - Info about Jupyter notebook"
        exit 1
        ;;
esac
