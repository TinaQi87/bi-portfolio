"""
Pipeline Triggers - Different ways to start the pipeline
Supports: Schedule (cron), Event-based (S3), Manual, Watchdog
"""
import time
import schedule
from datetime import datetime
from typing import Callable
import boto3
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from pipeline import DataPipeline, PipelineResult
from notifications import notify, logger


class ScheduleTrigger:
    """Run pipeline on a schedule (like cron)."""
    
    def __init__(self, pipeline_func: Callable):
        self.pipeline_func = pipeline_func
    
    def run_daily(self, at_time: str = "02:00"):
        """Run pipeline daily at specified time."""
        schedule.every().day.at(at_time).do(self.pipeline_func)
        logger.info(f"Scheduled daily run at {at_time}")
        self._run_scheduler()
    
    def run_hourly(self):
        """Run pipeline every hour."""
        schedule.every().hour.do(self.pipeline_func)
        logger.info("Scheduled hourly run")
        self._run_scheduler()
    
    def run_every(self, minutes: int):
        """Run pipeline every N minutes."""
        schedule.every(minutes).minutes.do(self.pipeline_func)
        logger.info(f"Scheduled run every {minutes} minutes")
        self._run_scheduler()
    
    def _run_scheduler(self):
        """Keep scheduler running."""
        logger.info("Scheduler started. Press Ctrl+C to stop.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped")


class S3EventTrigger:
    """Trigger pipeline when new files arrive in S3."""
    
    def __init__(self, bucket: str, prefix: str, pipeline_func: Callable):
        self.bucket = bucket
        self.prefix = prefix
        self.pipeline_func = pipeline_func
        self.sqs = boto3.client('sqs')
        self.queue_url = None
    
    def setup_s3_notifications(self, queue_url: str):
        """
        Setup S3 event notifications to SQS.
        Note: S3 bucket notification must be configured separately.
        """
        self.queue_url = queue_url
        logger.info(f"Listening for S3 events on {self.bucket}/{self.prefix}")
    
    def listen(self):
        """Poll SQS for S3 events and trigger pipeline."""
        if not self.queue_url:
            raise ValueError("Queue URL not set. Call setup_s3_notifications first.")
        
        logger.info("Starting S3 event listener...")
        
        while True:
            try:
                response = self.sqs.receive_message(
                    QueueUrl=self.queue_url,
                    MaxNumberOfMessages=10,
                    WaitTimeSeconds=20  # Long polling
                )
                
                for message in response.get('Messages', []):
                    body = json.loads(message['Body'])
                    
                    # Check if it's an S3 event
                    if 'Records' in body:
                        for record in body['Records']:
                            if record.get('eventSource') == 'aws:s3':
                                key = record['s3']['object']['key']
                                if key.startswith(self.prefix):
                                    logger.info(f"New file detected: {key}")
                                    self.pipeline_func()
                    
                    # Delete processed message
                    self.sqs.delete_message(
                        QueueUrl=self.queue_url,
                        ReceiptHandle=message['ReceiptHandle']
                    )
                    
            except Exception as e:
                logger.error(f"Error processing S3 event: {e}")
                time.sleep(5)


class FileWatchTrigger(FileSystemEventHandler):
    """Trigger pipeline when local files change (for development)."""
    
    def __init__(self, pipeline_func: Callable, watch_path: str = "./data/sources"):
        self.pipeline_func = pipeline_func
        self.watch_path = watch_path
        self.last_run = None
        self.cooldown = 60  # Minimum seconds between runs
    
    def on_created(self, event):
        """Handle new file creation."""
        if event.is_directory:
            return
        
        # Cooldown to prevent multiple triggers
        now = datetime.now()
        if self.last_run and (now - self.last_run).seconds < self.cooldown:
            return
        
        logger.info(f"New file detected: {event.src_path}")
        self.last_run = now
        self.pipeline_func()
    
    def start(self):
        """Start watching for file changes."""
        observer = Observer()
        observer.schedule(self, self.watch_path, recursive=True)
        observer.start()
        
        logger.info(f"Watching for changes in {self.watch_path}")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


def run_pipeline():
    """Wrapper function to run the pipeline."""
    pipeline = DataPipeline()
    return pipeline.run_full_pipeline()


# Example usage
if __name__ == "__main__":
    import sys
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "manual"
    
    if mode == "schedule":
        # Run daily at 2 AM
        trigger = ScheduleTrigger(run_pipeline)
        trigger.run_daily("02:00")
    
    elif mode == "watch":
        # Watch local directory for new files
        trigger = FileWatchTrigger(run_pipeline)
        trigger.start()
    
    elif mode == "s3":
        # Listen for S3 events
        trigger = S3EventTrigger(
            bucket="tina-data-lake",
            prefix="incoming/",
            pipeline_func=run_pipeline
        )
        trigger.setup_s3_notifications("https://sqs.ap-southeast-2.amazonaws.com/123456789/pipeline-trigger")
        trigger.listen()
    
    else:
        # Manual run
        result = run_pipeline()
        print(f"Pipeline completed: {result.status.value}")
