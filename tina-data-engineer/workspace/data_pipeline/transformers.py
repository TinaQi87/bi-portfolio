"""
Data Transformers - Clean and transform data
Bronze → Silver: Data cleansing, validation, standardization
Silver → Gold: Business logic, aggregations (via dbt)
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Callable, Optional
from datetime import datetime
import subprocess
import os

from notifications import notify, logger


class DataCleaner:
    """Clean and validate data for Silver zone."""
    
    @staticmethod
    def remove_duplicates(df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
        """Remove duplicate rows."""
        before = len(df)
        df = df.drop_duplicates(subset=subset)
        removed = before - len(df)
        if removed > 0:
            logger.info(f"Removed {removed} duplicate rows")
        return df
    
    @staticmethod
    def handle_nulls(df: pd.DataFrame, strategy: Dict[str, str] = None) -> pd.DataFrame:
        """
        Handle null values with different strategies per column.
        
        Strategies: 'drop', 'mean', 'median', 'mode', 'zero', 'empty', 'ffill'
        """
        strategy = strategy or {}
        
        for col, method in strategy.items():
            if col not in df.columns:
                continue
            
            null_count = df[col].isnull().sum()
            if null_count == 0:
                continue
            
            if method == 'drop':
                df = df.dropna(subset=[col])
            elif method == 'mean':
                df[col] = df[col].fillna(df[col].mean())
            elif method == 'median':
                df[col] = df[col].fillna(df[col].median())
            elif method == 'mode':
                df[col] = df[col].fillna(df[col].mode()[0])
            elif method == 'zero':
                df[col] = df[col].fillna(0)
            elif method == 'empty':
                df[col] = df[col].fillna('')
            elif method == 'ffill':
                df[col] = df[col].fillna(method='ffill')
            
            logger.info(f"Handled {null_count} nulls in '{col}' using '{method}'")
        
        return df
    
    @staticmethod
    def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names: lowercase, underscores."""
        df.columns = (df.columns
                      .str.lower()
                      .str.replace(' ', '_')
                      .str.replace('-', '_')
                      .str.replace('.', '_'))
        return df
    
    @staticmethod
    def convert_types(df: pd.DataFrame, type_map: Dict[str, str]) -> pd.DataFrame:
        """
        Convert column data types.
        
        type_map: {'column_name': 'int', 'date_col': 'datetime'}
        """
        for col, dtype in type_map.items():
            if col not in df.columns:
                continue
            try:
                if dtype == 'datetime':
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                elif dtype == 'int':
                    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
                elif dtype == 'float':
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                elif dtype == 'str':
                    df[col] = df[col].astype(str)
                elif dtype == 'bool':
                    df[col] = df[col].astype(bool)
            except Exception as e:
                logger.warning(f"Type conversion failed for {col}: {e}")
        return df
    
    @staticmethod
    def validate_data(df: pd.DataFrame, rules: Dict[str, Callable]) -> pd.DataFrame:
        """
        Validate data against rules, flag invalid rows.
        
        rules: {'column': lambda x: x > 0}  # Returns True if valid
        """
        df['_is_valid'] = True
        df['_validation_errors'] = ''
        
        for col, rule in rules.items():
            if col not in df.columns:
                continue
            
            invalid_mask = ~df[col].apply(rule)
            invalid_count = invalid_mask.sum()
            
            if invalid_count > 0:
                df.loc[invalid_mask, '_is_valid'] = False
                df.loc[invalid_mask, '_validation_errors'] += f"{col}: failed validation; "
                logger.warning(f"Validation failed for {invalid_count} rows in '{col}'")
        
        return df
    
    @staticmethod
    def trim_strings(df: pd.DataFrame) -> pd.DataFrame:
        """Trim whitespace from string columns."""
        str_cols = df.select_dtypes(include=['object']).columns
        for col in str_cols:
            try:
                df[col] = df[col].astype(str).str.strip()
            except Exception:
                pass  # Skip columns that can't be trimmed
        return df


class DataTransformer:
    """Transform data for Gold zone."""
    
    @staticmethod
    def add_surrogate_key(df: pd.DataFrame, key_name: str = 'sk_id') -> pd.DataFrame:
        """Add surrogate key column."""
        df[key_name] = range(1, len(df) + 1)
        return df
    
    @staticmethod
    def add_audit_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Add standard audit columns."""
        df['created_at'] = datetime.now()
        df['updated_at'] = datetime.now()
        df['etl_batch_id'] = datetime.now().strftime('%Y%m%d%H%M%S')
        return df
    
    @staticmethod
    def create_date_dimension(start_date: str, end_date: str) -> pd.DataFrame:
        """Generate date dimension table."""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        df = pd.DataFrame({'date': dates})
        df['date_key'] = df['date'].dt.strftime('%Y%m%d').astype(int)
        df['year'] = df['date'].dt.year
        df['quarter'] = df['date'].dt.quarter
        df['month'] = df['date'].dt.month
        df['month_name'] = df['date'].dt.month_name()
        df['week'] = df['date'].dt.isocalendar().week
        df['day'] = df['date'].dt.day
        df['day_name'] = df['date'].dt.day_name()
        df['day_of_week'] = df['date'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6])
        
        return df


class DBTRunner:
    """Run dbt transformations for Silver → Gold."""
    
    def __init__(self, project_dir: str):
        self.project_dir = project_dir
    
    def run(self, models: List[str] = None, full_refresh: bool = False) -> bool:
        """
        Run dbt models.
        
        Args:
            models: Specific models to run, or None for all
            full_refresh: Whether to do full refresh
        """
        cmd = ["dbt", "run"]
        
        if models:
            cmd.extend(["--select", " ".join(models)])
        if full_refresh:
            cmd.append("--full-refresh")
        
        try:
            logger.info(f"Running dbt: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("dbt run completed successfully")
            logger.debug(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            notify(f"dbt run failed: {e.stderr}", "error", ["log", "slack"])
            return False
    
    def test(self) -> bool:
        """Run dbt tests."""
        try:
            result = subprocess.run(
                ["dbt", "test"],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("dbt tests passed")
            return True
        except subprocess.CalledProcessError as e:
            notify(f"dbt tests failed: {e.stderr}", "error", ["log", "slack"])
            return False
