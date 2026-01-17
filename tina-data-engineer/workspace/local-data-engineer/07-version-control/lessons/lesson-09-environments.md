# Lesson 9: Environment Management

## The "Works on My Machine" Problem

Developer: "The pipeline works perfectly on my laptop."
Ops: "It's failing in production."
Developer: "That's impossible, I just ran it."

The difference? Environments.

---

## What Are Environments?

Environments are separate instances of your system with different purposes:

| Environment | Purpose | Data | Who Uses It |
|-------------|---------|------|-------------|
| **Local/Dev** | Development, experimentation | Sample/fake data | Individual developers |
| **Test/QA** | Automated testing | Test fixtures | CI/CD systems |
| **Staging** | Pre-production validation | Production-like data | QA team, stakeholders |
| **Production** | Real business operations | Real data | End users, systems |

---

## Why Separate Environments?

### Without Separation
- Test on production data → accidentally delete real records
- Debug on production → slow down real users
- Deploy untested code → break the business

### With Separation
- Break things safely in dev/staging
- Test with realistic data before production
- Validate changes with stakeholders
- Rollback production without losing test work

---

## Environment-Specific Configuration

The same code runs in all environments. What changes is **configuration**.

### Pattern 1: Environment Variables

```python
import os

# Configuration from environment
config = {
    'database_host': os.getenv('DB_HOST', 'localhost'),
    'database_name': os.getenv('DB_NAME', 'dev_db'),
    'api_key': os.getenv('API_KEY'),
    'debug': os.getenv('DEBUG', 'false').lower() == 'true'
}

# Usage
connection = connect(
    host=config['database_host'],
    database=config['database_name']
)
```

Set differently per environment:

```bash
# Local development
export DB_HOST=localhost
export DB_NAME=dev_db
export DEBUG=true

# Production
export DB_HOST=prod-db.company.com
export DB_NAME=production
export DEBUG=false
```

### Pattern 2: Config Files

```yaml
# config/development.yaml
database:
  host: localhost
  port: 5432
  name: dev_db

logging:
  level: DEBUG

features:
  new_algorithm: true  # Test new features in dev
```

```yaml
# config/production.yaml
database:
  host: prod-db.company.com
  port: 5432
  name: production

logging:
  level: WARNING

features:
  new_algorithm: false  # Not ready for production
```

```python
import yaml
import os

def load_config():
    env = os.getenv('ENVIRONMENT', 'development')
    with open(f'config/{env}.yaml') as f:
        return yaml.safe_load(f)

config = load_config()
```

### Pattern 3: .env Files

```bash
# .env.development
DB_HOST=localhost
DB_NAME=dev_db
DEBUG=true

# .env.production
DB_HOST=prod-db.company.com
DB_NAME=production
DEBUG=false
```

```python
from dotenv import load_dotenv
import os

# Load environment-specific .env
env = os.getenv('ENVIRONMENT', 'development')
load_dotenv(f'.env.{env}')
```

---

## Managing Secrets Across Environments

**Never commit secrets to Git.** Use:

### Local Development
```bash
# .env.local (gitignored)
DB_PASSWORD=local_dev_password
API_KEY=test_key_12345
```

### CI/CD
GitHub Secrets, GitLab CI Variables, etc.

### Production
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- Environment variables set by deployment system

```python
import boto3
import os

def get_secret(name):
    """Get secret from AWS Secrets Manager or environment."""
    # Try environment first (for local dev)
    env_value = os.getenv(name)
    if env_value:
        return env_value
    
    # Fall back to Secrets Manager (for production)
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=name)
    return response['SecretString']
```

---

## Database Per Environment

Each environment should have its own database:

```
Development:  dev-db.company.internal     / dev_warehouse
Staging:      staging-db.company.internal / staging_warehouse
Production:   prod-db.company.internal    / prod_warehouse
```

### Why Separate Databases?

1. **Isolation** - Dev experiments don't affect production
2. **Different data** - Dev can have sample data, staging has sanitized production copy
3. **Different permissions** - Developers can't accidentally query production
4. **Different scale** - Dev database can be smaller/cheaper

---

## Branching Strategy + Environments

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  feature/* ──┬──► develop ──► staging ──► main ──► prod    │
│              │                                               │
│  fix/*    ───┘                                              │
│                                                              │
│  Branch        │   Branch      │  Branch    │  Branch       │
│  Environment:  │   Environment:│  Env:      │  Env:         │
│  Local         │   Dev server  │  Staging   │  Production   │
│                │               │  server    │  server       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

| Branch | Deploys To | Automatically? |
|--------|------------|----------------|
| feature/* | Local only | No |
| develop | Dev environment | Yes (on merge) |
| staging | Staging environment | Yes (on merge) |
| main | Production | Yes or manual approval |

---

## Promoting Changes Through Environments

### Step 1: Develop Locally
```bash
# On feature branch, using local config
ENVIRONMENT=development python run_pipeline.py
```

### Step 2: Merge to Develop → Deploy to Dev
```bash
# CI/CD automatically deploys
# Tests run against dev database
```

### Step 3: Merge to Staging → Deploy to Staging
```bash
# Stakeholders validate
# Performance testing
# Integration testing with other systems
```

### Step 4: Merge to Main → Deploy to Production
```bash
# Final deployment
# Monitoring for issues
# Rollback plan ready
```

---

## Environment Parity

Keep environments as similar as possible:

### Same
- Code version
- Dependencies (requirements.txt)
- Schema structure
- Configuration structure

### Different
- Data (production has real data)
- Scale (production has more resources)
- Secrets (different credentials per environment)
- External integrations (test vs real APIs)

---

## Practical Example: Multi-Environment Pipeline

```python
# config.py
import os
from dataclasses import dataclass

@dataclass
class Config:
    environment: str
    db_host: str
    db_name: str
    db_password: str
    log_level: str
    batch_size: int

def load_config() -> Config:
    env = os.getenv('ENVIRONMENT', 'development')
    
    configs = {
        'development': Config(
            environment='development',
            db_host='localhost',
            db_name='dev_db',
            db_password=os.getenv('DB_PASSWORD', 'dev_password'),
            log_level='DEBUG',
            batch_size=100  # Small for fast iteration
        ),
        'staging': Config(
            environment='staging',
            db_host=os.getenv('DB_HOST'),
            db_name='staging_db',
            db_password=os.getenv('DB_PASSWORD'),
            log_level='INFO',
            batch_size=1000
        ),
        'production': Config(
            environment='production',
            db_host=os.getenv('DB_HOST'),
            db_name='prod_db',
            db_password=os.getenv('DB_PASSWORD'),
            log_level='WARNING',
            batch_size=10000  # Large for efficiency
        )
    }
    
    return configs.get(env, configs['development'])
```

```python
# pipeline.py
from config import load_config
import logging

config = load_config()

# Configure logging based on environment
logging.basicConfig(level=getattr(logging, config.log_level))
logger = logging.getLogger(__name__)

def run_pipeline():
    logger.info(f"Running in {config.environment} environment")
    logger.info(f"Connecting to {config.db_host}/{config.db_name}")
    logger.info(f"Batch size: {config.batch_size}")
    
    # Pipeline logic here...

if __name__ == '__main__':
    run_pipeline()
```

---

## Common Mistakes Beginners Make

1. **Hardcoding production values** - Always use configuration, never hardcode hosts/credentials

2. **Testing on production** - Even "just a quick test" can cause outages

3. **Same credentials everywhere** - Each environment should have unique credentials

4. **Skipping staging** - "It worked in dev" is not enough validation

5. **Environment config in code** - Keep config separate from code (files, env vars)

---

## Check Your Understanding

1. **Why have a staging environment if you already have dev?**
   <details><summary>Answer</summary>Dev is for individual development. Staging is production-like - same scale, similar data, integration with other systems. It catches issues dev misses.</details>

2. **Your pipeline works in dev but fails in production. What's likely different?**
   <details><summary>Answer</summary>Data volume (production has more), data quality (real data has edge cases), permissions, network access, resource limits, or external service differences.</details>

3. **Should you commit `.env.production` to Git?**
   <details><summary>Answer</summary>No! It contains secrets. Commit `.env.template` showing required variables without values. Set actual values through deployment system.</details>

4. **Why use environment variables instead of hardcoding?**
   <details><summary>Answer</summary>Same code runs everywhere. Change behavior by changing config, not code. Secrets stay out of Git. Easy to update without redeploying.</details>

5. **A bug is found in production. Where do you fix it?**
   <details><summary>Answer</summary>Create a fix branch, test locally, merge through normal process (dev → staging → production). For critical issues, you might fast-track but still test in staging first.</details>

---

## Quick Reference

| Environment | Database | Config Source | Deployment |
|-------------|----------|---------------|------------|
| Local | localhost | .env.local | Manual |
| Dev | dev-db | CI/CD secrets | On merge to develop |
| Staging | staging-db | CI/CD secrets | On merge to staging |
| Production | prod-db | Secrets Manager | On merge to main |

---

## What's Next

You understand all the pieces. The final lesson brings everything together in a complete workflow walkthrough.

[Next: Lesson 10 - Putting It Together →](lesson-10-complete-workflow.md)
