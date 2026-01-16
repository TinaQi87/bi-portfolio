# Lesson 4: Pandas Optimization

## Check Memory Usage

```python
df.info(memory_usage='deep')
df.memory_usage(deep=True)
```

---

## Optimize Data Types

```python
# Before
df['id'] = df['id'].astype('int32')  # Instead of int64
df['amount'] = df['amount'].astype('float32')  # Instead of float64

# Categories for low-cardinality strings
df['status'] = df['status'].astype('category')

# Auto-optimize
def optimize_df(df):
    for col in df.select_dtypes(include=['int64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='integer')
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='float')
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].nunique() / len(df) < 0.5:
            df[col] = df[col].astype('category')
    return df
```

---

## Avoid Loops

```python
# Bad
for i, row in df.iterrows():
    df.loc[i, 'new'] = row['a'] + row['b']

# Good
df['new'] = df['a'] + df['b']

# If you must iterate, use apply
df['new'] = df.apply(lambda row: row['a'] + row['b'], axis=1)
```

---

## Read Only What You Need

```python
# Read specific columns
df = pd.read_csv('file.csv', usecols=['id', 'name', 'amount'])

# Read in chunks
for chunk in pd.read_csv('huge.csv', chunksize=10000):
    process(chunk)

# Skip rows
df = pd.read_csv('file.csv', skiprows=range(1, 1000))
```

---

## Query vs Boolean Indexing

```python
# Both work, query can be faster for complex conditions
df_filtered = df[df['amount'] > 100]
df_filtered = df.query('amount > 100')
```

---

## Merge Optimization

```python
# Sort before merge if doing multiple merges
df1 = df1.sort_values('key')
df2 = df2.sort_values('key')
result = pd.merge(df1, df2, on='key')
```

---

## Key Takeaways

1. Use smaller data types
2. Use category for repeated strings
3. Avoid iterrows - use vectorized ops
4. Read only needed columns
5. Process in chunks for large files
