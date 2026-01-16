# Lesson 10: Building Production-Ready Pipelines

## What Makes a Pipeline "Production-Ready"?

A production pipeline runs reliably without human intervention. It handles errors gracefully, recovers from failures, and alerts the team when something goes wrong.

**The difference**:
- **Development pipeline**: Works on your laptop with sample data
- **Production pipeline**: Runs at 3 AM, handles 10 million rows, recovers from network failures, and pages you only when truly necessary

---

## Production Pipeline Architecture

```python
import logging
from datetime import datetime
import sys

class ProductionETL:
    def __init__(self, config):
        self.config = config
        self.setup_logging()
        self.metrics = {'start': None, 'end': None, 'rows': 0, 'errors': 0}
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"etl_{datetime.now():%Y%m%d}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """Main entry point"""
        self.metrics['start'] = datetime.now()
        self.logger.info(f"Starting ETL: {self.config['name']}")
        
        try:
            # Extract
            data = self.extract()
            
            # Transform
            transformed = self.transform(data)
            
            # Validate
            if not self.validate(transformed):
                raise ValueError("Data validation failed")
            
            # Load
            self.load(transformed)
            
            self.metrics['end'] = datetime.now()
            self.report_success()
            
        except Exception as e:
            self.metrics['errors'] += 1
            self.logger.error(f"Pipeline failed: {e}")
            self.alert_team(str(e))
            sys.exit(1)
    
    def extract(self):
        self.logger.info("Extracting data...")
        # Implementation here
        pass
    
    def transform(self, data):
        self.logger.info("Transforming data...")
        # Implementation here
        pass
    
    def validate(self, data):
        self.logger.info("Validating data...")
        # Implementation here
        return True
    
    def load(self, data):
        self.logger.info("Loading data...")
        # Implementation here
        pass
    
    def report_success(self):
        duration = self.metrics['end'] - self.metrics['start']
        self.logger.info(f"ETL completed in {duration}")
        self.logger.info(f"Rows processed: {self.metrics['rows']}")
    
    def alert_team(self, message):
        # Send email/Slack/PagerDuty alert
        self.logger.critical(f"ALERT: {message}")
```

---

## Configuration Management

Never hardcode connection strings or credentials:

```python
# config.py
import os
from dataclasses import dataclass

@dataclass
class Config:
    # Database settings from environment
    db_host: str = os.getenv('DB_HOST', 'localhost')
    db_user: str = os.getenv('DB_USER', 'devuser')
    db_pass: str = os.getenv('DB_PASSWORD', '')
    db_name: str = os.getenv('DB_NAME', 'devdb')
    
    # ETL settings
    batch_size: int = int(os.getenv('BATCH_SIZE', '10000'))
    max_retries: int = int(os.getenv('MAX_RETRIES', '3'))
    
    # Feature flags
    dry_run: bool = os.getenv('DRY_RUN', 'false').lower() == 'true'

# Usage
config = Config()
print(f"Connecting to {config.db_host}/{config.db_name}")
```

---

## Retry Logic

Network failures happen. Good pipelines retry:

```python
import time

def retry(max_attempts=3, delay=5, backoff=2):
    """Decorator for retry logic"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            current_delay = delay
            
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise
                    logging.warning(f"Attempt {attempts} failed: {e}. Retrying in {current_delay}s")
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator

@retry(max_attempts=3, delay=5)
def fetch_from_api(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()
```

---

## Checkpointing for Recovery

Save progress so you can resume after failures:

```python
import json

class CheckpointManager:
    def __init__(self, checkpoint_file):
        self.file = checkpoint_file
    
    def save(self, state):
        with open(self.file, 'w') as f:
            json.dump(state, f)
    
    def load(self):
        try:
            with open(self.file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    def clear(self):
        import os
        if os.path.exists(self.file):
            os.remove(self.file)

# Usage in ETL
checkpoint = CheckpointManager('etl_checkpoint.json')

# Resume from checkpoint if exists
state = checkpoint.load()
start_id = state['last_id'] if state else 0

for batch in get_batches(start_id=start_id):
    process_batch(batch)
    checkpoint.save({'last_id': batch[-1]['id']})

checkpoint.clear()  # Success - remove checkpoint
```

---

## Idempotency

Running the same pipeline twice should produce the same result:

```python
def load_idempotent(df, table_name, key_column, conn):
    """Load data idempotently using UPSERT pattern"""
    
    for _, row in df.iterrows():
        # Delete existing record if present
        conn.execute(f"""
            DELETE FROM {table_name} 
            WHERE {key_column} = %s
        """, (row[key_column],))
        
        # Insert new record
        columns = ', '.join(row.index)
        placeholders = ', '.join(['%s'] * len(row))
        conn.execute(f"""
            INSERT INTO {table_name} ({columns})
            VALUES ({placeholders})
        """, tuple(row))
    
    conn.commit()
```

---

## Complete Production Pipeline

```python
#!/usr/bin/env python3
"""Production ETL Pipeline - Sales Data"""

import pandas as pd
import logging
from datetime import datetime
import sys
import os

# Configuration
CONFIG = {
    'name': 'sales_etl',
    'source': os.getenv('SOURCE_PATH', 'data/sales.csv'),
    'db_host': os.getenv('DB_HOST', 'mysql'),
    'db_name': os.getenv('DB_NAME', 'devdb'),
    'batch_size': 5000
}

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    start = datetime.now()
    logger.info(f"Starting {CONFIG['name']}")
    
    try:
        # Extract
        logger.info(f"Reading from {CONFIG['source']}")
        df = pd.read_csv(CONFIG['source'])
        logger.info(f"Extracted {len(df)} rows")
        
        # Transform
        df['processed_at'] = datetime.now()
        df['amount'] = df['amount'].fillna(0)
        logger.info("Transformations complete")
        
        # Validate
        assert df['id'].notna().all(), "Null IDs found"
        assert (df['amount'] >= 0).all(), "Negative amounts found"
        logger.info("Validation passed")
        
        # Load
        # (database load code here)
        logger.info(f"Loaded {len(df)} rows")
        
        duration = datetime.now() - start
        logger.info(f"ETL completed in {duration}")
        
    except Exception as e:
        logger.error(f"ETL FAILED: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

---

## Key Takeaways

1. **Configuration**: Use environment variables, never hardcode secrets
2. **Logging**: Log everything - you'll need it at 3 AM
3. **Retry logic**: Network failures are normal, handle them
4. **Checkpointing**: Save progress for recovery
5. **Idempotency**: Same input = same output, always
6. **Alerting**: Know when things break

---

## What's Next?

You now have all the building blocks for production ETL:
- Extract from multiple sources
- Transform and clean data
- Load with different strategies
- Handle errors gracefully
- Log and monitor
- Process incrementally
- Test thoroughly
- Build production-ready code

In the exercises, you'll put it all together!

---

## Common Mistakes

| Mistake | Better Approach |
|---------|-----------------|
| Hardcoded credentials | Use environment variables |
| No retry logic | Retry with exponential backoff |
| Pipeline can't resume | Add checkpointing |
| Running twice creates duplicates | Make it idempotent |
| Silent failures | Alert on errors |
