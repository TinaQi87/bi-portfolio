# Module 05: Supplementary Data Sources - Newbee Guide

## 🤔 What Is This Module About?

Real data doesn't come from just one place. This module teaches you to handle data from different sources and formats - XML from legacy systems, JSON from APIs - and combine them into your data lake.

---

## 📚 Concepts Explained (Like You're 5)

### Why Multiple Data Sources?

**Simple:** Companies have many systems, each storing data differently.

**Real example:**
- Student records in MySQL database
- Attendance from old system (XML files)
- School info from API (JSON)
- Partner data via email (CSV)

**Your job:** Make them all work together.

### What is XML?

**Simple:** A text format for storing data using tags (like HTML).

**Example:**
```xml
<Student>
    <Name>John</Name>
    <Age>20</Age>
    <Score>85</Score>
</Student>
```

**Why it exists:** Created in 1998, used heavily in enterprise systems. Many government and healthcare systems still use it.

**Pros:** Human-readable, self-describing
**Cons:** Verbose (lots of text), complex to parse

### What is JSON?

**Simple:** A text format for storing data using key-value pairs (like Python dictionaries).

**Example:**
```json
{
    "name": "John",
    "age": 20,
    "score": 85
}
```

**Why it's popular:** Simpler than XML, native to JavaScript, used by most modern APIs.

**Pros:** Compact, easy to parse, widely supported
**Cons:** No comments allowed, less strict than XML

### XML vs JSON - Quick Comparison

| Feature | XML | JSON |
|---------|-----|------|
| Age | Old (1998) | Newer (2001) |
| Verbosity | Very verbose | Compact |
| Parsing | Complex | Simple |
| Used by | Legacy systems, enterprises | Modern APIs, web apps |
| Example | `<name>John</name>` | `"name": "John"` |

### What is Parsing?

**Simple:** Reading a file format and converting it to something your code can use.

**Analogy:** Parsing is like translating a foreign language into your native language.

```
XML File                    Python Dictionary
┌─────────────────┐        ┌─────────────────┐
│ <Name>John</Name>│  ───►  │ {"name": "John"}│
└─────────────────┘        └─────────────────┘
        Parsing
```

### What is Flattening?

**Simple:** Converting nested/hierarchical data into flat rows and columns.

**Why needed:** Databases and analytics tools work with tables (rows and columns), not nested structures.

```
Nested (hard to query):              Flat (easy to query):
{                                    student_id | course | score
  "student": {                       -----------|--------|------
    "id": 1,                         1          | Math   | 85
    "courses": [                     1          | Science| 90
      {"name": "Math", "score": 85},
      {"name": "Science", "score": 90}
    ]
  }
}
```

### What is Data Integration?

**Simple:** Combining data from multiple sources into one unified view.

**Challenges:**
1. Different formats (XML, JSON, CSV)
2. Different schemas (column names don't match)
3. Different IDs (student_id vs studentID vs id)
4. Different quality (some sources have more errors)

### What is an API?

**Simple:** A way for programs to talk to each other over the internet.

**Analogy:** An API is like a waiter in a restaurant. You (the program) tell the waiter (API) what you want, and they bring it from the kitchen (server).

```
Your Code                    API                     Server
┌─────────┐    Request      ┌─────┐    Query       ┌─────────┐
│ Python  │ ──────────────► │ API │ ────────────►  │ Database│
│ Script  │ ◄────────────── │     │ ◄────────────  │         │
└─────────┘    Response     └─────┘    Results     └─────────┘
              (JSON)
```

### What is a Legacy System?

**Simple:** An old system that's still in use because it works and replacing it is expensive/risky.

**Examples:**
- 20-year-old attendance system that exports XML
- COBOL programs running bank transactions
- Old databases that can't be upgraded

**Reality:** You WILL work with legacy systems. They're everywhere.

---

## 🛠️ What Each File Does

### `scripts/generate_attendance_xml.py`

**Purpose:** Creates fake XML attendance data (simulating a legacy system)

**Why generate fake data?** We don't have a real legacy system, so we simulate one for practice.

**Includes intentional issues:**
- Missing values
- Invalid dates
- Duplicates

### `scripts/generate_schools_json.py`

**Purpose:** Creates fake JSON school data (simulating an API response)

**What it generates:**
- School names and IDs
- Regions
- Contact information

### `src/bronze/xml_extractor.py`

**Purpose:** Reads XML files and converts to Parquet

**What it does:**
1. Find all XML files in a folder
2. Parse each file
3. Extract records
4. Convert to DataFrame
5. Save as Parquet

### `src/bronze/json_extractor.py`

**Purpose:** Reads JSON files and converts to Parquet

**Similar to XML extractor but for JSON format.**

### `src/silver/supplementary_loader.py`

**Purpose:** Loads supplementary data into Iceberg tables

**What it does:**
1. Read Parquet from Bronze
2. Clean and validate
3. Load into Silver Iceberg tables

---

## 🎯 Why Do We Need This?

### The Problem

Data lives in many places:
- Main database (MySQL)
- Legacy systems (XML exports)
- External APIs (JSON)
- Partner files (CSV)

Each has different formats, schemas, and quality levels.

### The Solution

Build extractors for each source type:
1. Parse the format (XML, JSON, CSV)
2. Flatten to tabular structure
3. Load to Bronze (raw)
4. Clean and load to Silver

---

## 👀 Three Perspectives

### What a Newbee Sees
"Why can't everyone just use the same format? XML looks complicated. Why do we need to handle so many different sources?"

### What a Senior Data Engineer Sees
"Good practice handling multiple formats. The XML parser handles namespaces correctly. I'd add schema validation for JSON. The error handling for malformed files is important."

### What a Head of Data Sees
"This demonstrates real-world integration skills. The ability to onboard new data sources quickly is valuable. Good foundation for a data catalog that tracks all sources."

---

## 🔑 Key Takeaways for Newbees

1. **Data comes from everywhere** - Expect multiple formats
2. **XML = Legacy** - Old but still common in enterprises
3. **JSON = Modern** - APIs and web services
4. **Parsing = Translation** - Convert formats to usable data
5. **Flattening = Simplification** - Nested → Tabular

---

## ❓ Common Newbee Questions

**Q: Why do legacy systems still use XML?**
A: 
1. They work and are stable
2. Replacing them is expensive and risky
3. Many regulations require keeping old systems
4. "If it ain't broke, don't fix it"

**Q: Why not just ask the source to change their format?**
A: 
1. You often can't control external sources
2. Legacy systems can't be easily modified
3. Partners have their own standards
4. Your job is to adapt, not demand

**Q: How do I know which format a file is?**
A:
1. File extension (.xml, .json, .csv)
2. Look at the first few characters
3. Try parsing and catch errors
4. Ask the data provider

**Q: What if the XML/JSON structure changes?**
A:
1. Your parser might break
2. Add validation to detect changes
3. Alert when unexpected structure found
4. Version your parsers

**Q: Why flatten nested data?**
A:
1. SQL works with tables, not trees
2. Analytics tools expect rows and columns
3. Easier to join with other data
4. Better query performance

---

## 🔍 Code Patterns

### Parsing XML
```python
import xml.etree.ElementTree as ET

# Parse XML file
tree = ET.parse('attendance.xml')
root = tree.getroot()

# Extract data
for record in root.findall('.//AttendanceRecord'):
    student_id = record.find('StudentID').text
    status = record.find('Status').text
```

### Parsing JSON
```python
import json

# Parse JSON file
with open('schools.json') as f:
    data = json.load(f)

# Extract data
for school in data['schools']:
    name = school['name']
    region = school['region']
```

---

## 📖 Terms Glossary

| Term | Simple Definition |
|------|-------------------|
| XML | Text format using tags (like HTML) |
| JSON | Text format using key-value pairs |
| Parsing | Converting file format to usable data |
| Flattening | Converting nested data to rows/columns |
| API | Way for programs to communicate |
| Legacy System | Old system still in use |
| Data Integration | Combining data from multiple sources |
| Namespace | XML feature for avoiding name conflicts |
| Schema | Structure defining data format |
| Extractor | Code that reads from a data source |
