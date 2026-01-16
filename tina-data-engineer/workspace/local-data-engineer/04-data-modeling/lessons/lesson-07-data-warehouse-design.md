# Lesson 7: Data Warehouse Design

## What is a Data Warehouse?

A data warehouse is a central repository for integrated data from multiple sources, optimized for analysis and reporting.

**Key characteristics:**
- Subject-oriented (organized by business area)
- Integrated (data from multiple sources)
- Time-variant (historical data)
- Non-volatile (read-mostly, stable)

---

## Data Warehouse Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │   ERP   │  │   CRM   │  │  Files  │  │  APIs   │            │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘            │
└───────┼────────────┼────────────┼────────────┼──────────────────┘
        │            │            │            │
        └────────────┴─────┬──────┴────────────┘
                           │
                    ┌──────▼──────┐
                    │   STAGING   │  ← Raw data landing
                    │    AREA     │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ INTEGRATION │  ← Clean, transform, integrate
                    │    LAYER    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │PRESENTATION │  ← Star schemas, data marts
                    │    LAYER    │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
   │ Reports │       │   BI    │       │Analytics│
   └─────────┘       │  Tools  │       └─────────┘
                     └─────────┘
```

---

## The Three Layers

### 1. Staging Area

**Purpose:** Land raw data from sources

**Characteristics:**
- Exact copy of source data
- No transformations
- Truncate and reload
- Temporary storage

```sql
-- Staging table mirrors source
CREATE TABLE stg_orders (
    order_id VARCHAR(50),
    customer_id VARCHAR(50),
    order_date VARCHAR(50),  -- Keep as string initially
    amount VARCHAR(50),
    status VARCHAR(50),
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Integration Layer (ODS/DWH)

**Purpose:** Clean, transform, integrate data

**Characteristics:**
- Data cleansing applied
- Business rules applied
- Data types corrected
- Duplicates removed
- History tracked

```sql
-- Integrated table with proper types
CREATE TABLE int_orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    amount DECIMAL(10,2),
    status VARCHAR(20),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### 3. Presentation Layer (Data Marts)

**Purpose:** Serve business users and BI tools

**Characteristics:**
- Star schemas
- Optimized for queries
- Business-friendly names
- Pre-aggregated tables

```sql
-- Star schema for sales analysis
CREATE TABLE fact_sales (...);
CREATE TABLE dim_customer (...);
CREATE TABLE dim_product (...);
CREATE TABLE dim_date (...);
```

---

## Data Mart

A data mart is a subset of the data warehouse focused on one business area.

```
                    ┌─────────────────┐
                    │  Data Warehouse │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐         ┌────▼────┐         ┌────▼────┐
   │  Sales  │         │Marketing│         │ Finance │
   │Data Mart│         │Data Mart│         │Data Mart│
   └─────────┘         └─────────┘         └─────────┘
```

**Benefits:**
- Faster queries (smaller dataset)
- Tailored to department needs
- Easier security management

---

## ETL vs ELT

### ETL (Extract, Transform, Load)
Transform data BEFORE loading to warehouse.

```
Source → Extract → Transform → Load → Warehouse
```

**Use when:**
- Limited warehouse compute
- Complex transformations
- Data cleansing needed before load

### ELT (Extract, Load, Transform)
Load raw data, then transform IN the warehouse.

```
Source → Extract → Load → Transform → Warehouse
```

**Use when:**
- Powerful warehouse (cloud DW)
- Want raw data preserved
- Transformations change frequently

---

## Kimball vs Inmon

Two main approaches to data warehouse design:

### Kimball (Bottom-Up)
- Build data marts first
- Star schemas
- Faster to implement
- Business-driven

```
Data Marts → Conformed Dimensions → Enterprise DW
```

### Inmon (Top-Down)
- Build enterprise DW first
- Normalized (3NF)
- More planning upfront
- IT-driven

```
Enterprise DW (3NF) → Data Marts (Star Schema)
```

**Most common today:** Kimball approach with star schemas.

---

## Naming Conventions

### Tables
```
stg_     Staging tables
int_     Integration layer
dim_     Dimension tables
fact_    Fact tables
rpt_     Report tables
agg_     Aggregate tables
```

### Examples
```sql
stg_orders          -- Staging: raw orders
int_orders          -- Integration: cleaned orders
dim_customer        -- Dimension: customer
fact_sales          -- Fact: sales transactions
agg_daily_sales     -- Aggregate: daily sales summary
rpt_monthly_revenue -- Report: monthly revenue
```

---

## Schema Organization

```sql
-- Create schemas for each layer
CREATE SCHEMA staging;
CREATE SCHEMA integration;
CREATE SCHEMA presentation;
CREATE SCHEMA reporting;

-- Tables in schemas
staging.stg_orders
integration.int_orders
presentation.dim_customer
presentation.fact_sales
reporting.rpt_monthly_sales
```

---

## Metadata

Track information about your data:

```sql
CREATE TABLE etl_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    table_name VARCHAR(100),
    load_start TIMESTAMP,
    load_end TIMESTAMP,
    rows_inserted INT,
    rows_updated INT,
    rows_deleted INT,
    status VARCHAR(20),
    error_message TEXT
);

CREATE TABLE data_dictionary (
    table_name VARCHAR(100),
    column_name VARCHAR(100),
    data_type VARCHAR(50),
    description TEXT,
    source_system VARCHAR(100),
    business_owner VARCHAR(100)
);
```

---

## Simple Data Warehouse Example

### Staging
```sql
CREATE TABLE stg_sales (
    order_id VARCHAR(50),
    order_date VARCHAR(50),
    customer_id VARCHAR(50),
    customer_name VARCHAR(200),
    product_id VARCHAR(50),
    product_name VARCHAR(200),
    quantity VARCHAR(50),
    price VARCHAR(50),
    load_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Integration
```sql
CREATE TABLE int_sales (
    order_id INT PRIMARY KEY,
    order_date DATE,
    customer_id INT,
    product_id INT,
    quantity INT,
    price DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Presentation (Star Schema)
```sql
CREATE TABLE dim_date (...);
CREATE TABLE dim_customer (...);
CREATE TABLE dim_product (...);

CREATE TABLE fact_sales (
    sale_key INT PRIMARY KEY AUTO_INCREMENT,
    date_key INT,
    customer_key INT,
    product_key INT,
    quantity INT,
    unit_price DECIMAL(10,2),
    total_amount DECIMAL(10,2)
);
```

---

## Key Takeaways

✅ Data warehouse has three layers: staging, integration, presentation
✅ Staging holds raw data from sources
✅ Integration layer cleans and transforms
✅ Presentation layer serves users (star schemas)
✅ Data marts focus on specific business areas
✅ Use consistent naming conventions
✅ Track metadata for governance

---

## Next Lesson

In Lesson 8, you'll learn when to denormalize for performance!
