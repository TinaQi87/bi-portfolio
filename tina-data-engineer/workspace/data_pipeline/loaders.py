"""
Data Loaders - Write data to destinations
Destinations: PostgreSQL Data Warehouse, S3
"""
import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
from typing import List, Optional
from datetime import datetime

from config import POSTGRES_CONFIG, BATCH_SIZE
from notifications import notify, logger


class PostgresLoader:
    """Load data into PostgreSQL data warehouse."""
    
    def __init__(self, config: dict = POSTGRES_CONFIG):
        self.config = config
        self.conn = None
    
    def connect(self):
        """Establish connection."""
        self.conn = psycopg2.connect(**self.config)
        logger.info("Connected to PostgreSQL warehouse")
    
    def close(self):
        """Close connection."""
        if self.conn:
            self.conn.close()
    
    def create_table_from_df(self, df: pd.DataFrame, table_name: str, schema: str = "public"):
        """Create table based on DataFrame schema."""
        if not self.conn:
            self.connect()
        
        # Map pandas dtypes to PostgreSQL types
        type_map = {
            'int64': 'BIGINT',
            'Int64': 'BIGINT',
            'float64': 'DOUBLE PRECISION',
            'object': 'TEXT',
            'bool': 'BOOLEAN',
            'datetime64[ns]': 'TIMESTAMP',
            'datetime64[ns, UTC]': 'TIMESTAMPTZ'
        }
        
        columns = []
        for col, dtype in df.dtypes.items():
            pg_type = type_map.get(str(dtype), 'TEXT')
            columns.append(f'"{col}" {pg_type}')
        
        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {schema}.{table_name} (
                {', '.join(columns)}
            )
        """
        
        with self.conn.cursor() as cur:
            cur.execute(create_sql)
        self.conn.commit()
        logger.info(f"Created table {schema}.{table_name}")
    
    def load(self, df: pd.DataFrame, table_name: str, schema: str = "public",
             if_exists: str = "append", batch_size: int = BATCH_SIZE) -> int:
        """
        Load DataFrame to PostgreSQL table.
        
        Args:
            df: DataFrame to load
            table_name: Target table name
            schema: Database schema
            if_exists: 'append', 'replace', or 'fail'
            batch_size: Rows per batch insert
        
        Returns:
            Number of rows loaded
        """
        if not self.conn:
            self.connect()
        
        if if_exists == 'replace':
            # Use TRUNCATE instead of DROP to preserve dependent views
            with self.conn.cursor() as cur:
                try:
                    cur.execute(f"TRUNCATE TABLE {schema}.{table_name}")
                except:
                    pass  # Table doesn't exist yet
            self.conn.commit()
        
        self.create_table_from_df(df, table_name, schema)
        
        # Prepare data for insertion
        columns = [f'"{col}"' for col in df.columns]
        values = [tuple(row) for row in df.values]
        
        insert_sql = f"""
            INSERT INTO {schema}.{table_name} ({', '.join(columns)})
            VALUES %s
        """
        
        rows_loaded = 0
        with self.conn.cursor() as cur:
            # Batch insert for performance
            for i in range(0, len(values), batch_size):
                batch = values[i:i + batch_size]
                execute_values(cur, insert_sql, batch)
                rows_loaded += len(batch)
                logger.info(f"Loaded {rows_loaded}/{len(values)} rows")
        
        self.conn.commit()
        logger.info(f"Completed loading {rows_loaded} rows to {schema}.{table_name}")
        return rows_loaded
    
    def upsert(self, df: pd.DataFrame, table_name: str, key_columns: List[str],
               schema: str = "public") -> int:
        """
        Upsert (insert or update) data based on key columns.
        
        This is common for slowly changing dimensions (SCD Type 1).
        """
        if not self.conn:
            self.connect()
        
        self.create_table_from_df(df, table_name, schema)
        
        columns = list(df.columns)
        update_cols = [c for c in columns if c not in key_columns]
        
        # Build upsert SQL
        insert_cols = ', '.join([f'"{c}"' for c in columns])
        conflict_cols = ', '.join([f'"{c}"' for c in key_columns])
        update_set = ', '.join([f'"{c}" = EXCLUDED."{c}"' for c in update_cols])
        
        upsert_sql = f"""
            INSERT INTO {schema}.{table_name} ({insert_cols})
            VALUES %s
            ON CONFLICT ({conflict_cols})
            DO UPDATE SET {update_set}
        """
        
        values = [tuple(row) for row in df.values]
        
        with self.conn.cursor() as cur:
            execute_values(cur, upsert_sql, values)
        
        self.conn.commit()
        logger.info(f"Upserted {len(values)} rows to {schema}.{table_name}")
        return len(values)
    
    def execute_sql(self, query: str) -> Optional[pd.DataFrame]:
        """Execute arbitrary SQL."""
        if not self.conn:
            self.connect()
        
        with self.conn.cursor() as cur:
            cur.execute(query)
            if cur.description:  # SELECT query
                columns = [desc[0] for desc in cur.description]
                return pd.DataFrame(cur.fetchall(), columns=columns)
            self.conn.commit()
            return None
