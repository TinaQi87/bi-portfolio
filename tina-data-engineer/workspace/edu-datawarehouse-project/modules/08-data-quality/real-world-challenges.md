# Module 08: Data Quality Framework - Real-World Challenges

## Scale Comparison

| Metric | This Project | Production Scale |
|--------|--------------|------------------|
| Quality checks | 13 | 500-2,000+ |
| Tables monitored | 6 | 100-500+ |
| Quarantine records | 1 | 10,000s daily |
| Alert channels | Console | Slack, PagerDuty, Email |
| Check frequency | On-demand | Continuous |

---

## Production Challenges You'd Face

### 1. Great Expectations Integration

**Your Project:** Custom quality checks

**Production Reality:**
- Need standardized, shareable expectations
- Version-controlled data contracts
- Auto-generated documentation

**Solution - Great Expectations:**
```python
import great_expectations as gx

context = gx.get_context()
validator = context.sources.pandas_default.read_dataframe(df)

validator.expect_column_values_to_not_be_null("student_id")
validator.expect_column_values_to_be_between("score", 0, 100)
validator.expect_column_values_to_be_in_set("gender", ["M", "F"])

result = validator.validate()
```

### 2. Data Contracts Between Teams

**Your Project:** Single developer

**Production Reality:**
- Multiple teams produce/consume data
- Schema changes break downstream
- Need formal contracts

**Solution - Data Contracts:**
```yaml
# contracts/students.yaml
name: students
version: 2.0.0
owner: data-platform-team
schema:
  - name: student_id
    type: integer
    nullable: false
    tests:
      - unique
      - not_null
  - name: gender
    type: string
    allowed_values: [M, F]
sla:
  freshness: 6 hours
  completeness: 99.9%
```

### 3. Anomaly Detection

**Your Project:** Static thresholds

**Production Reality:**
- Normal varies by day/season
- Need ML-based anomaly detection
- Alert on statistical outliers

**Solution:**
```python
from scipy import stats

def detect_anomaly(current_count, historical_counts):
    mean = np.mean(historical_counts)
    std = np.std(historical_counts)
    z_score = (current_count - mean) / std
    
    if abs(z_score) > 3:  # 3 sigma rule
        return True, f"Count {current_count} is {z_score:.1f} std from mean"
    return False, "Normal"
```

### 4. Data Lineage & Impact Analysis

**Your Project:** Manual tracking

**Production Reality:**
- Need to know what breaks if source changes
- Regulatory requirements (GDPR, SOX)
- Root cause analysis

**Solution - OpenLineage:**
```python
from openlineage.client import OpenLineageClient

client = OpenLineageClient(url="http://marquez:5000")

# Emit lineage event
client.emit(
    RunEvent(
        inputs=[Dataset("bronze", "students")],
        outputs=[Dataset("silver", "dim_student")],
        job=Job("transform_students")
    )
)
```

### 5. Real-time Quality Monitoring

**Your Project:** Batch checks

**Production Reality:**
- Streaming data needs real-time validation
- Can't wait for batch to catch issues
- Need dashboards and metrics

**Solution - Prometheus + Grafana:**
```python
from prometheus_client import Counter, Gauge

quality_checks_total = Counter('quality_checks_total', 'Total checks', ['table', 'check', 'status'])
null_rate = Gauge('null_rate', 'Null rate by column', ['table', 'column'])

# In your check
quality_checks_total.labels(table='students', check='not_null', status='pass').inc()
null_rate.labels(table='students', column='email').set(0.05)
```

---

## Interview Questions & Answers

### Q1: "What are the six dimensions of data quality?"

**Answer:**
"The six dimensions are:

| Dimension | Question | Example |
|-----------|----------|---------|
| **Completeness** | Is all data present? | No NULL in required fields |
| **Accuracy** | Is data correct? | Email format valid |
| **Consistency** | Does data agree? | Same customer in two tables |
| **Timeliness** | Is data fresh? | Updated within SLA |
| **Uniqueness** | No duplicates? | One row per customer |
| **Validity** | Follows rules? | Age between 0-150 |

In this project, I implemented checks for all six: not_null (completeness), range checks (accuracy), referential integrity (consistency), freshness checks (timeliness), unique checks (uniqueness), and value set validation (validity)."

### Q2: "How do you handle bad data without losing it?"

**Answer:**
"I implement a quarantine pattern:

1. **Detect** - Quality checks identify bad records
2. **Isolate** - Move to quarantine table with metadata
3. **Alert** - Notify data stewards
4. **Review** - Manual inspection of quarantined data
5. **Fix** - Correct source or apply transformation
6. **Reprocess** - Mark as reprocessed, reload

```python
class QuarantineManager:
    def quarantine_records(self, df, source, reason):
        # Store as JSONB with metadata
        for row in df.iterrows():
            insert_to_quarantine(source, row.to_json(), reason)
```

This preserves data for debugging while keeping the pipeline clean."

### Q3: "How would you implement data quality at scale?"

**Answer:**
"At scale, I'd use:

1. **Great Expectations** - Standardized expectations, auto-docs
2. **dbt tests** - SQL-based tests in transformation layer
3. **Monte Carlo/Datafold** - ML-based anomaly detection
4. **Prometheus/Grafana** - Metrics and dashboards
5. **PagerDuty** - Alerting with escalation

Architecture:
```
Source → Quality Gate → Bronze → Quality Gate → Silver → dbt tests → Gold
              ↓                      ↓                      ↓
         Quarantine            Quarantine              Alerts
```"

### Q4: "What's the difference between data quality and data observability?"

**Answer:**
"| Aspect | Data Quality | Data Observability |
|--------|--------------|-------------------|
| **Focus** | Is data correct? | Is pipeline healthy? |
| **Checks** | Schema, values, rules | Freshness, volume, lineage |
| **Timing** | Point-in-time | Continuous monitoring |
| **Tools** | Great Expectations, dbt | Monte Carlo, Datadog |

Data quality asks 'Is this data valid?' while observability asks 'Is something wrong with my data system?'

In this project, I implemented both: quality checks (validation) and pipeline monitoring (observability)."

### Q5: "How do you prioritize which quality checks to implement?"

**Answer:**
"I prioritize based on business impact:

1. **Critical** - Breaks downstream, financial impact
   - Primary keys not null
   - Referential integrity
   
2. **High** - Affects reports, user-facing
   - Required fields complete
   - Values in valid range
   
3. **Medium** - Data quality issues
   - Duplicates
   - Format validation
   
4. **Low** - Nice to have
   - Consistency across sources
   - Historical comparisons

Start with critical checks, add others iteratively based on incidents."

---

## Common Mistakes to Avoid

1. **Too many alerts**
   - Alert fatigue leads to ignored alerts
   - Only alert on actionable issues

2. **No quarantine**
   - Deleting bad data loses debugging info
   - Always preserve for analysis

3. **Static thresholds**
   - "Row count > 1000" breaks on holidays
   - Use statistical methods

4. **No ownership**
   - Quality issues need owners
   - Define data stewards per domain

5. **Checking too late**
   - Catch issues at ingestion, not reporting
   - Shift quality left

---

## Tools Used in Production

| Tool | Purpose | Alternative |
|------|---------|-------------|
| Custom Python | Quality checks | Great Expectations |
| PostgreSQL | Quarantine storage | S3 + Athena |
| Console | Alerting | Slack, PagerDuty |

**Production would add:**
- Great Expectations for standardized checks
- Monte Carlo for data observability
- dbt tests for transformation layer
- Datadog/Grafana for dashboards
- PagerDuty for on-call alerting
