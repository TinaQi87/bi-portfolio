#!/bin/bash
# run_in_docker.sh - Run pipeline commands inside tina-devtools container
#
# Usage:
#   ./run_in_docker.sh validate    # Check all connections
#   ./run_in_docker.sh pipeline    # Run full ETL pipeline
#   ./run_in_docker.sh generate    # Generate delta data (new records)
#   ./run_in_docker.sh dbt         # Run dbt transformations
#   ./run_in_docker.sh verify      # Verify record counts
#   ./run_in_docker.sh shell       # Open interactive shell

CONTAINER="tina-devtools"
WORKDIR="/workspace/tina-data-engineer/workspace/data_pipeline"
DBT_DIR="/workspace/tina-data-engineer/workspace/data_pipeline/dbt_project"

case "$1" in
    validate)
        echo "🔍 Running validation..."
        docker exec -w $WORKDIR $CONTAINER python3 validate.py
        ;;
    pipeline)
        echo "🚀 Running pipeline..."
        docker exec -w $WORKDIR $CONTAINER python3 pipeline.py
        ;;
    generate)
        echo "🔄 Generating delta data..."
        docker exec -w $WORKDIR $CONTAINER python3 generate_delta.py
        ;;
    dbt)
        echo "🔧 Running dbt transformations..."
        docker exec -w $DBT_DIR $CONTAINER dbt run --profiles-dir .
        ;;
    dbt-test)
        echo "🧪 Running dbt tests..."
        docker exec -w $DBT_DIR $CONTAINER dbt test --profiles-dir .
        ;;
    verify)
        echo "📊 Verifying data counts..."
        docker exec -w $WORKDIR $CONTAINER python3 verify.py
        ;;
    full)
        echo "🔄 Running full incremental cycle..."
        echo ""
        $0 generate
        echo ""
        $0 pipeline
        echo ""
        $0 dbt
        echo ""
        $0 verify
        ;;
    shell)
        echo "🐚 Opening shell in container..."
        docker exec -it -w $WORKDIR $CONTAINER bash
        ;;
    *)
        echo "Usage: $0 {validate|pipeline|generate|dbt|verify|full|shell}"
        echo ""
        echo "Commands:"
        echo "  validate  - Check all connections (DB, MinIO, API)"
        echo "  pipeline  - Run the full ETL pipeline"
        echo "  generate  - Generate new delta data in MySQL"
        echo "  dbt       - Run dbt transformations (Silver → Gold)"
        echo "  verify    - Check record counts at each stage"
        echo "  full      - Run complete cycle: generate → pipeline → dbt → verify"
        echo "  shell     - Open bash shell in container"
        exit 1
        ;;
esac
