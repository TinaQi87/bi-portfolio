"""
Airflow DAG Template

Copy this template as a starting point for new DAGs.
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import logging

# Configure logging
logger = logging.getLogger(__name__)

# =============================================================================
# DEFAULT ARGUMENTS
# =============================================================================
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email': ['data-alerts@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
}

# =============================================================================
# TASK FUNCTIONS
# =============================================================================
def extract(**context):
    """
    Extract data from source.
    
    Uses execution_date for backfill compatibility.
    """
    execution_date = context['ds']
    logger.info(f"Extracting data for {execution_date}")
    
    # Your extraction logic here
    data = {'rows': 100, 'date': execution_date}
    
    logger.info(f"Extracted {data['rows']} rows")
    return data


def transform(**context):
    """
    Transform extracted data.
    
    Pulls data from extract task via XCom.
    """
    ti = context['ti']
    data = ti.xcom_pull(task_ids='extract')
    
    logger.info(f"Transforming {data['rows']} rows")
    
    # Your transformation logic here
    transformed = {
        'rows': data['rows'],
        'transformed': True
    }
    
    logger.info("Transform complete")
    return transformed


def load(**context):
    """
    Load transformed data to destination.
    
    Should be idempotent - safe to re-run.
    """
    ti = context['ti']
    data = ti.xcom_pull(task_ids='transform')
    execution_date = context['ds']
    
    logger.info(f"Loading {data['rows']} rows for {execution_date}")
    
    # Your load logic here
    # Remember: DELETE then INSERT, or use UPSERT for idempotency
    
    logger.info("Load complete")
    return {'loaded': data['rows']}


def notify_success(**context):
    """Send success notification."""
    ti = context['ti']
    load_result = ti.xcom_pull(task_ids='load')
    
    logger.info(f"Pipeline succeeded. Loaded {load_result['loaded']} rows.")
    # Add Slack/email notification here


def on_failure_callback(context):
    """Handle task failure."""
    task_id = context['task_instance'].task_id
    dag_id = context['dag'].dag_id
    execution_date = context['execution_date']
    exception = context.get('exception', 'Unknown error')
    
    logger.error(f"Task {dag_id}.{task_id} failed: {exception}")
    # Add alerting logic here (Slack, PagerDuty, etc.)


# =============================================================================
# DAG DEFINITION
# =============================================================================
with DAG(
    dag_id='template_etl_pipeline',
    default_args=default_args,
    description='Template ETL pipeline - copy and customize',
    start_date=datetime(2024, 1, 1),
    schedule='0 3 * * *',  # Daily at 3 AM UTC
    catchup=False,
    max_active_runs=1,
    tags=['template', 'etl'],
    doc_md="""
    ## Template ETL Pipeline
    
    This is a template DAG. Copy and customize for your use case.
    
    ### Schedule
    Runs daily at 3 AM UTC.
    
    ### Tasks
    1. **extract**: Pull data from source
    2. **transform**: Clean and transform data
    3. **load**: Load to destination
    4. **notify**: Send success notification
    
    ### Contacts
    - Owner: data-team@company.com
    - Slack: #data-pipelines
    """
) as dag:
    
    # Start marker
    start = EmptyOperator(task_id='start')
    
    # Main tasks
    extract_task = PythonOperator(
        task_id='extract',
        python_callable=extract,
        on_failure_callback=on_failure_callback
    )
    
    transform_task = PythonOperator(
        task_id='transform',
        python_callable=transform,
        on_failure_callback=on_failure_callback
    )
    
    load_task = PythonOperator(
        task_id='load',
        python_callable=load,
        on_failure_callback=on_failure_callback,
        sla=timedelta(hours=1)  # Alert if load takes > 1 hour
    )
    
    notify_task = PythonOperator(
        task_id='notify',
        python_callable=notify_success
    )
    
    # End marker
    end = EmptyOperator(task_id='end')
    
    # Define dependencies
    start >> extract_task >> transform_task >> load_task >> notify_task >> end
