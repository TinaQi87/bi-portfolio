# Module 05: Supplementary Data - Real-World Challenges

## Scale Comparison

| Metric | This Project | Production Scale |
|--------|--------------|------------------|
| XML files/day | 5 | 100-10,000+ |
| JSON API calls | 1 | 1,000s with pagination |
| File size | KB | GB per file |
| Sources | 2 | 10-50+ different systems |
| Formats | XML, JSON | XML, JSON, CSV, Avro, Protobuf, EDI |

---

## Production Challenges You'd Face

### 1. XML Namespaces

**Your Project:** Simple XML without namespaces

**Production Reality:**
```xml
<!-- Real enterprise XML has namespaces -->
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <ns1:GetStudentResponse xmlns:ns1="http://education.gov/api/v2">
      <ns1:Student>
        <ns1:ID>12345</ns1:ID>
      </ns1:Student>
    </ns1:GetStudentResponse>
  </soap:Body>
</soap:Envelope>
```

**Solution:**
```python
# Must handle namespaces explicitly
namespaces = {
    'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
    'ns1': 'http://education.gov/api/v2'
}
root.findall('.//ns1:Student', namespaces)
```

### 2. JSON Schema Drift

**Your Project:** Consistent JSON structure

**Production Reality:**
- API v1 returns `{"student_id": 123}`
- API v2 returns `{"studentId": 123}` (camelCase)
- Some records missing fields entirely
- New fields added without notice

**Solution:**
```python
def safe_extract(record, *keys, default=None):
    """Try multiple key names, return first found."""
    for key in keys:
        if key in record:
            return record[key]
    return default

# Usage
student_id = safe_extract(record, 'student_id', 'studentId', 'id')
```

### 3. Large File Streaming

**Your Project:** Load entire file into memory

**Production Reality:**
- 10GB XML files won't fit in memory
- Must stream and process in chunks

**Solution:**
```python
# Use iterparse for large XML
from xml.etree.ElementTree import iterparse

def stream_large_xml(filepath):
    for event, elem in iterparse(filepath, events=['end']):
        if elem.tag == 'Record':
            yield extract_record(elem)
            elem.clear()  # Free memory
```

### 4. API Rate Limiting

**Your Project:** Single JSON file

**Production Reality:**
- APIs limit requests (e.g., 100/minute)
- Must handle pagination
- Need retry logic for failures

**Solution:**
```python
import time
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(min=1, max=60), stop=stop_after_attempt(5))
def fetch_with_retry(url):
    response = requests.get(url)
    if response.status_code == 429:  # Rate limited
        raise Exception("Rate limited")
    return response.json()

def paginate_api(base_url):
    page = 1
    while True:
        data = fetch_with_retry(f"{base_url}?page={page}")
        if not data['results']:
            break
        yield from data['results']
        page += 1
        time.sleep(0.5)  # Be nice to the API
```

### 5. Character Encoding Issues

**Your Project:** UTF-8 everywhere

**Production Reality:**
- Legacy systems use Latin-1, Windows-1252
- Mixed encodings in same file
- BOM (Byte Order Mark) issues

**Solution:**
```python
import chardet

def detect_and_read(filepath):
    with open(filepath, 'rb') as f:
        raw = f.read()
        detected = chardet.detect(raw)
        return raw.decode(detected['encoding'])
```

---

## Interview Questions & Answers

### Q1: "How do you handle XML with namespaces?"

**Answer:**
"XML namespaces are common in enterprise systems like SOAP APIs. I handle them by:
1. Defining a namespace dictionary mapping prefixes to URIs
2. Passing this dictionary to all `find()` and `findall()` calls
3. Using `lxml` instead of ElementTree for complex namespace handling

In production, I'd also validate against XSD schemas to catch structural issues early."

### Q2: "What's your approach to integrating data from multiple sources?"

**Answer:**
"Multi-source integration requires:
1. **Schema mapping** - Document how each source maps to your target schema
2. **Data quality rules** - Define cleaning rules per source
3. **Source tracking** - Always track which source each record came from
4. **Idempotency** - Make loads repeatable without duplicates

In this project, I tracked `source_file` for XML records and applied source-specific cleaning rules."

### Q3: "How do you handle API pagination?"

**Answer:**
"APIs typically use cursor-based or offset-based pagination:

```python
# Cursor-based (preferred - consistent results)
cursor = None
while True:
    response = api.get(cursor=cursor)
    yield from response['data']
    cursor = response.get('next_cursor')
    if not cursor:
        break

# Offset-based (simpler but can miss/duplicate records)
offset = 0
while True:
    response = api.get(offset=offset, limit=100)
    if not response['data']:
        break
    yield from response['data']
    offset += 100
```

I prefer cursor-based because offset pagination can miss records if data changes during extraction."

### Q4: "How do you flatten nested JSON for analytics?"

**Answer:**
"Nested JSON must be flattened for SQL-based analytics. My approach:

1. **Simple nesting** - Prefix with parent name: `contact.email` → `contact_email`
2. **Arrays of primitives** - Join to string: `['A','B']` → `'A,B'`
3. **Arrays of objects** - Create separate table with foreign key
4. **Deeply nested** - Use `pandas.json_normalize()` for automatic flattening

In this project, I flattened `contact.email` to `contact_email` and joined `facilities` array to a comma-separated string."

### Q5: "What data quality issues do you expect from external sources?"

**Answer:**
"External sources commonly have:
1. **Missing fields** - Use `.get()` with defaults
2. **Type inconsistencies** - Same field as string vs number
3. **Invalid values** - Dates like '2026-02-30'
4. **Encoding issues** - Mixed UTF-8/Latin-1
5. **Schema changes** - New fields, renamed fields

In this project, I intentionally generated these issues and built cleaning logic to handle them - removing invalid dates, filling empty status with 'Unknown', and filtering marked duplicates."

---

## Common Mistakes to Avoid

1. **Loading entire file into memory**
   - Use streaming for large files
   - Process in chunks

2. **Ignoring namespaces in XML**
   - Enterprise XML always has namespaces
   - Test with real data early

3. **Hardcoding field names**
   - APIs change field names between versions
   - Use flexible extraction with fallbacks

4. **No retry logic for APIs**
   - Networks fail, APIs rate-limit
   - Always implement exponential backoff

5. **Assuming consistent encoding**
   - Detect encoding, don't assume UTF-8
   - Handle BOM characters

---

## Tools Used in Production

| Tool | Purpose | Alternative |
|------|---------|-------------|
| ElementTree | Simple XML parsing | lxml (faster, more features) |
| json | JSON parsing | orjson (faster), ujson |
| pandas | Data manipulation | Polars (faster for large data) |
| requests | HTTP client | httpx (async support) |

**Production would add:**
- Apache NiFi for data flow orchestration
- AWS Glue for serverless ETL
- Airbyte/Fivetran for managed connectors
- Great Expectations for data validation
