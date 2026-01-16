# Lesson 4: Advanced Transformations

## Joins and Lookups

### Merge DataFrames (SQL-like JOIN)
```python
# Inner join
df = pd.merge(orders, customers, on="customer_id")

# Left join
df = pd.merge(orders, customers, on="customer_id", how="left")

# Join on different column names
df = pd.merge(orders, customers, 
              left_on="cust_id", right_on="customer_id")

# Multiple join keys
df = pd.merge(orders, products, on=["product_id", "warehouse_id"])
```

### Lookup Values
```python
# Create lookup dictionary
customer_names = customers.set_index("customer_id")["name"].to_dict()

# Apply lookup
orders["customer_name"] = orders["customer_id"].map(customer_names)

# With default for missing
orders["customer_name"] = orders["customer_id"].map(
    lambda x: customer_names.get(x, "Unknown")
)
```

### Enrich with Reference Data
```python
def enrich_orders(orders, customers, products):
    """Add customer and product details to orders"""
    
    # Add customer info
    df = pd.merge(
        orders,
        customers[["customer_id", "name", "segment"]],
        on="customer_id",
        how="left"
    )
    
    # Add product info
    df = pd.merge(
        df,
        products[["product_id", "product_name", "category"]],
        on="product_id",
        how="left"
    )
    
    return df
```

---

## Aggregations

### Basic Aggregations
```python
# Single aggregation
total_sales = df["amount"].sum()
avg_order = df["amount"].mean()

# Group by
sales_by_customer = df.groupby("customer_id")["amount"].sum()

# Multiple aggregations
summary = df.groupby("customer_id").agg({
    "order_id": "count",
    "amount": ["sum", "mean", "min", "max"]
})
```

### Named Aggregations
```python
summary = df.groupby("customer_id").agg(
    order_count=("order_id", "count"),
    total_amount=("amount", "sum"),
    avg_amount=("amount", "mean"),
    first_order=("order_date", "min"),
    last_order=("order_date", "max")
).reset_index()
```

### Rolling Aggregations
```python
# Sort by date first
df = df.sort_values("order_date")

# 7-day rolling average
df["rolling_avg"] = df["amount"].rolling(window=7).mean()

# Rolling sum by customer
df["customer_running_total"] = df.groupby("customer_id")["amount"].cumsum()
```

---

## Pivoting Data

### Pivot Table
```python
# Rows: customer, Columns: month, Values: sum of amount
pivot = df.pivot_table(
    values="amount",
    index="customer_id",
    columns="month",
    aggfunc="sum",
    fill_value=0
)
```

### Unpivot (Melt)
```python
# Wide to long format
wide_df = pd.DataFrame({
    "customer": ["A", "B"],
    "jan_sales": [100, 200],
    "feb_sales": [150, 250]
})

long_df = pd.melt(
    wide_df,
    id_vars=["customer"],
    value_vars=["jan_sales", "feb_sales"],
    var_name="month",
    value_name="sales"
)
```

---

## Window Functions

```python
# Rank within group
df["rank"] = df.groupby("category")["amount"].rank(ascending=False)

# Percent of total
df["pct_of_total"] = df["amount"] / df["amount"].sum() * 100

# Percent of group total
df["pct_of_category"] = df.groupby("category")["amount"].transform(
    lambda x: x / x.sum() * 100
)

# Lag/Lead
df["prev_amount"] = df.groupby("customer_id")["amount"].shift(1)
df["next_amount"] = df.groupby("customer_id")["amount"].shift(-1)

# Difference from previous
df["change"] = df["amount"] - df["prev_amount"]
```

---

## Date Transformations

```python
# Extract components
df["year"] = df["order_date"].dt.year
df["month"] = df["order_date"].dt.month
df["day"] = df["order_date"].dt.day
df["weekday"] = df["order_date"].dt.day_name()
df["quarter"] = df["order_date"].dt.quarter

# Date calculations
df["days_since_order"] = (pd.Timestamp.now() - df["order_date"]).dt.days

# Date formatting
df["month_year"] = df["order_date"].dt.strftime("%Y-%m")

# Fiscal year (if FY starts in July)
df["fiscal_year"] = df["order_date"].apply(
    lambda x: x.year if x.month >= 7 else x.year - 1
)
```

---

## Building Dimension Tables

### Customer Dimension
```python
def build_dim_customer(orders, customers):
    """Build customer dimension from source data"""
    
    # Start with customer master
    dim = customers.copy()
    
    # Add aggregated metrics from orders
    order_stats = orders.groupby("customer_id").agg(
        total_orders=("order_id", "count"),
        total_spent=("amount", "sum"),
        first_order=("order_date", "min"),
        last_order=("order_date", "max")
    ).reset_index()
    
    dim = pd.merge(dim, order_stats, on="customer_id", how="left")
    
    # Fill nulls for customers with no orders
    dim["total_orders"] = dim["total_orders"].fillna(0).astype(int)
    dim["total_spent"] = dim["total_spent"].fillna(0)
    
    # Add derived columns
    dim["customer_segment"] = pd.cut(
        dim["total_spent"],
        bins=[0, 100, 500, float("inf")],
        labels=["Bronze", "Silver", "Gold"]
    )
    
    # Add surrogate key
    dim["customer_key"] = range(1, len(dim) + 1)
    
    return dim
```

### Date Dimension
```python
def build_dim_date(start_date, end_date):
    """Build date dimension"""
    
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    
    dim = pd.DataFrame({"full_date": dates})
    dim["date_key"] = dim["full_date"].dt.strftime("%Y%m%d").astype(int)
    dim["year"] = dim["full_date"].dt.year
    dim["quarter"] = dim["full_date"].dt.quarter
    dim["month"] = dim["full_date"].dt.month
    dim["month_name"] = dim["full_date"].dt.month_name()
    dim["day"] = dim["full_date"].dt.day
    dim["day_name"] = dim["full_date"].dt.day_name()
    dim["is_weekend"] = dim["full_date"].dt.dayofweek >= 5
    
    return dim
```

---

## Building Fact Tables

```python
def build_fact_sales(orders, dim_customer, dim_product, dim_date):
    """Build sales fact table"""
    
    fact = orders.copy()
    
    # Look up dimension keys
    customer_lookup = dim_customer.set_index("customer_id")["customer_key"].to_dict()
    product_lookup = dim_product.set_index("product_id")["product_key"].to_dict()
    
    fact["customer_key"] = fact["customer_id"].map(customer_lookup)
    fact["product_key"] = fact["product_id"].map(product_lookup)
    fact["date_key"] = fact["order_date"].dt.strftime("%Y%m%d").astype(int)
    
    # Handle missing lookups
    fact["customer_key"] = fact["customer_key"].fillna(0).astype(int)
    fact["product_key"] = fact["product_key"].fillna(0).astype(int)
    
    # Calculate measures
    fact["line_total"] = fact["quantity"] * fact["unit_price"]
    
    # Select final columns
    fact = fact[[
        "date_key", "customer_key", "product_key",
        "order_id", "quantity", "unit_price", "line_total"
    ]]
    
    return fact
```

---

## Practical Example: Complete Transform

```python
def transform_sales_data(orders, customers, products):
    """Complete transformation pipeline"""
    
    # 1. Clean orders
    orders = orders.drop_duplicates(subset=["order_id"])
    orders["order_date"] = pd.to_datetime(orders["order_date"])
    orders["quantity"] = pd.to_numeric(orders["quantity"], errors="coerce").fillna(1)
    orders["unit_price"] = pd.to_numeric(orders["unit_price"], errors="coerce").fillna(0)
    
    # 2. Enrich with lookups
    df = pd.merge(orders, customers[["customer_id", "name", "city"]], 
                  on="customer_id", how="left")
    df = pd.merge(df, products[["product_id", "product_name", "category"]], 
                  on="product_id", how="left")
    
    # 3. Calculate measures
    df["line_total"] = df["quantity"] * df["unit_price"]
    
    # 4. Add date dimensions
    df["order_year"] = df["order_date"].dt.year
    df["order_month"] = df["order_date"].dt.strftime("%Y-%m")
    
    # 5. Categorize
    df["order_size"] = pd.cut(
        df["line_total"],
        bins=[0, 50, 200, float("inf")],
        labels=["Small", "Medium", "Large"]
    )
    
    # 6. Add metadata
    df["processed_at"] = pd.Timestamp.now()
    
    return df
```

---

## Key Takeaways

✅ Use merge for joins, map for lookups
✅ groupby + agg for aggregations
✅ pivot_table for reshaping data
✅ Window functions for rankings and running totals
✅ Build dimensions with surrogate keys
✅ Build facts with dimension key lookups

---

## Next Lesson

In Lesson 5, you'll learn loading strategies!
