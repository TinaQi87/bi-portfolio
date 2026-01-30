# Module 5: Supplementary Data Sources

## 🎯 Learning Objectives

By the end of this module, you will:
- Generate realistic XML and JSON data (simulating external feeds)
- Build parsers for different file formats
- Handle multi-source data integration challenges

---

## 📚 Concept: Multi-Source Integration

### Real-World Reality

In companies, data never comes from just one source:
- **Legacy systems** export XML (old, but still everywhere)
- **APIs** return JSON (modern systems)
- **Partners** send CSV via SFTP
- **Databases** have different schemas

Your job as a data engineer: **make them all work together**.

### Common Challenges

| Source Type | Challenge | Solution |
|-------------|-----------|----------|
| XML | Nested structures, namespaces | Flatten to tabular |
| JSON | Schema varies between records | Handle missing fields |
| CSV | Encoding issues, delimiter problems | Detect and handle |
| API | Rate limits, pagination | Retry logic, batching |

---

## 🛠️ Task 1: Generate XML Attendance Data

### Why XML?

Many legacy systems (government, healthcare, education) still use XML. You'll encounter it.

### Step 1.1: Create Attendance Data Generator

```bash
docker-compose exec devtools bash
cd /workspace/tina-data-engineer/workspace/edu-datawarehouse-project
```

```bash
cat > scripts/generate_attendance_xml.py << 'EOF'
"""
Generate XML Attendance Records

Simulates a legacy attendance system that exports daily XML files.
Includes intentional data quality issues for practice.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import random
from datetime import datetime, timedelta
import os

# Configuration
OUTPUT_DIR = "/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/generated/attendance"
NUM_DAYS = 5
STUDENTS_PER_DAY = 100

# Sample student IDs (subset from OULAD)
STUDENT_IDS = list(range(10000, 10500))

def generate_attendance_record(student_id: int, date: datetime) -> dict:
    """Generate a single attendance record with possible issues."""
    
    # Randomly introduce data quality issues
    issues = random.choices(
        ['none', 'missing_status', 'invalid_date', 'duplicate'],
        weights=[0.85, 0.05, 0.05, 0.05]
    )[0]
    
    record = {
        'student_id': student_id,
        'date': date.strftime('%Y-%m-%d'),
        'status': random.choice(['Present', 'Absent', 'Late', 'Excused']),
        'check_in_time': f"{random.randint(7,9):02d}:{random.randint(0,59):02d}:00",
        'notes': ''
    }
    
    # Introduce issues
    if issues == 'missing_status':
        record['status'] = ''
    elif issues == 'invalid_date':
        record['date'] = '2026-02-30'  # Invalid date
    elif issues == 'duplicate':
        record['notes'] = 'DUPLICATE_RECORD'
    
    return record

def generate_daily_xml(date: datetime) -> str:
    """Generate XML file for a single day."""
    
    root = ET.Element('AttendanceReport')
    root.set('generated', datetime.now().isoformat())
    root.set('school_id', 'SCH001')
    
    header = ET.SubElement(root, 'Header')
    ET.SubElement(header, 'ReportDate').text = date.strftime('%Y-%m-%d')
    ET.SubElement(header, 'System').text = 'LegacyAttendanceSystem v2.1'
    
    records = ET.SubElement(root, 'Records')
    
    # Generate records for random students
    selected_students = random.sample(STUDENT_IDS, STUDENTS_PER_DAY)
    
    for student_id in selected_students:
        record_data = generate_attendance_record(student_id, date)
        
        record = ET.SubElement(records, 'AttendanceRecord')
        ET.SubElement(record, 'StudentID').text = str(record_data['student_id'])
        ET.SubElement(record, 'Date').text = record_data['date']
        ET.SubElement(record, 'Status').text = record_data['status']
        ET.SubElement(record, 'CheckInTime').text = record_data['check_in_time']
        if record_data['notes']:
            ET.SubElement(record, 'Notes').text = record_data['notes']
    
    # Pretty print
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    return xml_str

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("Generating XML attendance files...")
    print("=" * 50)
    
    base_date = datetime.now() - timedelta(days=NUM_DAYS)
    
    for i in range(NUM_DAYS):
        date = base_date + timedelta(days=i)
        filename = f"attendance_{date.strftime('%Y%m%d')}.xml"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        xml_content = generate_daily_xml(date)
        
        with open(filepath, 'w') as f:
            f.write(xml_content)
        
        print(f"  Created: {filename}")
    
    print(f"\nGenerated {NUM_DAYS} XML files in {OUTPUT_DIR}")
    print("Note: Files contain intentional data quality issues for practice")

if __name__ == "__main__":
    main()
EOF
```

### Step 1.2: Generate the XML Files

```bash
python scripts/generate_attendance_xml.py
```

### Step 1.3: Inspect Generated XML

```bash
head -30 data/generated/attendance/attendance_*.xml | head -50
```

---

## 🛠️ Task 2: Generate JSON School Metadata

### Step 2.1: Create School Data Generator

```bash
cat > scripts/generate_schools_json.py << 'EOF'
"""
Generate JSON School Metadata

Simulates an API response with school/district information.
"""

import json
import random
import os

OUTPUT_DIR = "/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/generated/schools"

REGIONS = [
    'East Anglian Region', 'Scotland', 'North Western Region',
    'South East Region', 'West Midlands Region', 'Wales',
    'North Region', 'South West Region', 'East Midlands Region',
    'Yorkshire Region', 'London Region', 'Ireland'
]

def generate_schools():
    """Generate school metadata."""
    schools = []
    
    for i in range(1, 21):
        school = {
            'school_id': f'SCH{i:03d}',
            'school_name': f'District {i} Academy',
            'region': random.choice(REGIONS),
            'type': random.choice(['Primary', 'Secondary', 'Combined']),
            'capacity': random.randint(500, 2000),
            'established_year': random.randint(1950, 2010),
            'contact': {
                'email': f'admin@district{i}.edu',
                'phone': f'+44-{random.randint(100,999)}-{random.randint(1000,9999)}'
            },
            'facilities': random.sample(
                ['Library', 'Lab', 'Sports Hall', 'Cafeteria', 'Auditorium'],
                k=random.randint(2, 5)
            ),
            'active': random.choice([True, True, True, False])  # 75% active
        }
        schools.append(school)
    
    return {'schools': schools, 'generated_at': '2026-01-31T00:00:00Z'}

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    data = generate_schools()
    filepath = os.path.join(OUTPUT_DIR, 'schools_metadata.json')
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Generated: {filepath}")
    print(f"Schools: {len(data['schools'])}")

if __name__ == "__main__":
    main()
EOF
```

### Step 2.2: Generate JSON

```bash
python scripts/generate_schools_json.py
cat data/generated/schools/schools_metadata.json | head -40
```

---

## 🛠️ Task 3: Build XML Parser

### Step 3.1: Create XML Extractor

```bash
cat > src/bronze/xml_extractor.py << 'EOF'
"""
XML to Bronze Layer Extractor

Parses XML files and converts to Parquet for Bronze layer.
Handles common XML parsing challenges.
"""

import xml.etree.ElementTree as ET
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime
import os
import io
import sys

sys.path.append('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project')
from src.utils.connections import get_s3_client

class XMLExtractor:
    """Extract XML files to Bronze layer."""
    
    def __init__(self, bucket: str = "edu-bronze"):
        self.bucket = bucket
        self.s3 = get_s3_client()
        self.extraction_date = datetime.now().strftime("%Y-%m-%d")
    
    def parse_attendance_xml(self, filepath: str) -> pd.DataFrame:
        """Parse attendance XML file to DataFrame."""
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        records = []
        for record in root.findall('.//AttendanceRecord'):
            records.append({
                'student_id': record.findtext('StudentID'),
                'date': record.findtext('Date'),
                'status': record.findtext('Status'),
                'check_in_time': record.findtext('CheckInTime'),
                'notes': record.findtext('Notes', '')
            })
        
        return pd.DataFrame(records)
    
    def extract_attendance_files(self, source_dir: str) -> dict:
        """Extract all attendance XML files to Bronze."""
        all_records = []
        files_processed = 0
        
        for filename in sorted(os.listdir(source_dir)):
            if not filename.endswith('.xml'):
                continue
            
            filepath = os.path.join(source_dir, filename)
            df = self.parse_attendance_xml(filepath)
            df['source_file'] = filename
            all_records.append(df)
            files_processed += 1
            print(f"  Parsed: {filename} ({len(df)} records)")
        
        if not all_records:
            raise FileNotFoundError(f"No XML files in {source_dir}")
        
        # Combine all files
        combined_df = pd.concat(all_records, ignore_index=True)
        
        # Write to Bronze
        table = pa.Table.from_pandas(combined_df)
        buffer = io.BytesIO()
        pq.write_table(table, buffer)
        buffer.seek(0)
        
        s3_key = f"xml/attendance/{self.extraction_date}/attendance.parquet"
        self.s3.put_object(
            Bucket=self.bucket,
            Key=s3_key,
            Body=buffer.getvalue()
        )
        
        print(f"\n  → Uploaded to s3://{self.bucket}/{s3_key}")
        
        return {
            'files_processed': files_processed,
            'total_records': len(combined_df),
            's3_path': f"s3://{self.bucket}/{s3_key}"
        }


if __name__ == "__main__":
    extractor = XMLExtractor()
    
    print("Extracting XML attendance files...")
    print("=" * 50)
    
    source_dir = "/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/generated/attendance"
    result = extractor.extract_attendance_files(source_dir)
    
    print(f"\nSummary:")
    print(f"  Files: {result['files_processed']}")
    print(f"  Records: {result['total_records']}")
EOF
```

### Step 3.2: Run XML Extractor

```bash
python src/bronze/xml_extractor.py
```

---

## 🛠️ Task 4: Build JSON Parser

### Step 4.1: Create JSON Extractor

```bash
cat > src/bronze/json_extractor.py << 'EOF'
"""
JSON to Bronze Layer Extractor

Parses JSON files (including nested structures) to Parquet.
"""

import json
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime
import io
import sys

sys.path.append('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project')
from src.utils.connections import get_s3_client

class JSONExtractor:
    """Extract JSON files to Bronze layer."""
    
    def __init__(self, bucket: str = "edu-bronze"):
        self.bucket = bucket
        self.s3 = get_s3_client()
        self.extraction_date = datetime.now().strftime("%Y-%m-%d")
    
    def flatten_school(self, school: dict) -> dict:
        """Flatten nested school structure."""
        flat = {
            'school_id': school['school_id'],
            'school_name': school['school_name'],
            'region': school['region'],
            'type': school['type'],
            'capacity': school['capacity'],
            'established_year': school['established_year'],
            'contact_email': school.get('contact', {}).get('email'),
            'contact_phone': school.get('contact', {}).get('phone'),
            'facilities': ','.join(school.get('facilities', [])),
            'active': school.get('active', True)
        }
        return flat
    
    def extract_schools_json(self, filepath: str) -> dict:
        """Extract schools JSON to Bronze."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Flatten nested structure
        records = [self.flatten_school(s) for s in data['schools']]
        df = pd.DataFrame(records)
        
        # Write to Bronze
        table = pa.Table.from_pandas(df)
        buffer = io.BytesIO()
        pq.write_table(table, buffer)
        buffer.seek(0)
        
        s3_key = f"json/schools/{self.extraction_date}/schools.parquet"
        self.s3.put_object(
            Bucket=self.bucket,
            Key=s3_key,
            Body=buffer.getvalue()
        )
        
        print(f"  → Uploaded to s3://{self.bucket}/{s3_key}")
        
        return {
            'records': len(df),
            's3_path': f"s3://{self.bucket}/{s3_key}"
        }


if __name__ == "__main__":
    extractor = JSONExtractor()
    
    print("Extracting JSON school metadata...")
    print("=" * 50)
    
    filepath = "/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/generated/schools/schools_metadata.json"
    result = extractor.extract_schools_json(filepath)
    
    print(f"\nRecords extracted: {result['records']}")
EOF
```

### Step 4.2: Run JSON Extractor

```bash
python src/bronze/json_extractor.py
```

---

## ✅ Module 5 Checklist

- [ ] XML attendance files generated (5 days)
- [ ] JSON school metadata generated
- [ ] XML parser working (extracts to Bronze)
- [ ] JSON parser working (handles nested data)
- [ ] All supplementary data in Bronze bucket

---

## 🎓 Key Takeaways

1. **Real data is messy**: Multiple formats, nested structures, quality issues
2. **Flatten for analytics**: Nested JSON/XML → flat tables
3. **Preserve source info**: Track which file each record came from
4. **Handle missing fields**: Use `.get()` with defaults

---

## 🔜 Next: Module 6

In Module 6, we'll:
- Set up dbt project
- Create staging models
- Build dimension and fact tables in Gold layer

**When you've completed all checkpoints above, proceed to Module 6.**
