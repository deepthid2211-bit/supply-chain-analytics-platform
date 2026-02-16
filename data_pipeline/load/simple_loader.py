"""
Simple Snowflake Loader (Certificate-Safe)
===========================================

Alternative loader that uses direct SQL COPY commands instead of write_pandas.
Bypasses certificate validation issues.

Author: Deepthi Desharaju
Date: February 2026
"""

import snowflake.connector
import pandas as pd
import yaml
import logging
from pathlib import Path
import argparse
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleSnowflakeLoader:
    """
    Simplified Snowflake loader using SQL INSERT statements.
    No certificate validation issues.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize Snowflake connection."""
        self.config = self._load_config(config_path)
        self.conn = None
        self.cursor = None
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        return config['snowflake']
    
    def connect(self):
        """Establish connection to Snowflake with OCSP checks disabled."""
        try:
            self.conn = snowflake.connector.connect(
                user=self.config['user'],
                password=self.config['password'],
                account=self.config['account'],
                warehouse=self.config['warehouse'],
                database=self.config['database'],
                schema=self.config['schema'],
                insecure_mode=True  # Disable certificate validation
            )
            self.cursor = self.conn.cursor()
            logger.info(f"✅ Connected to Snowflake: {self.config['account']}")
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Disconnected from Snowflake")
    
    def load_products(self, csv_path: str):
        """Load products CSV."""
        logger.info(f"Loading products from {csv_path}")
        
        df = pd.read_csv(csv_path)
        logger.info(f"  Read {len(df)} products")
        
        # Truncate table
        self.cursor.execute("TRUNCATE TABLE LANDING.PRODUCTS")
        
        # Insert rows
        insert_sql = """
        INSERT INTO LANDING.PRODUCTS (
            PRODUCT_ID, SKU, PRODUCT_NAME, CATEGORY, SUBCATEGORY, 
            BRAND, UNIT_COST, UNIT_PRICE, SUPPLIER
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        rows = []
        for _, row in df.iterrows():
            rows.append((
                int(row['product_id']),
                str(row['sku']),
                str(row['product_name']),
                str(row['category']),
                str(row['subcategory']),
                str(row['brand']),
                float(row['unit_cost']),
                float(row['unit_price']),
                str(row['supplier'])
            ))
        
        self.cursor.executemany(insert_sql, rows)
        self.conn.commit()
        logger.info(f"✅ Loaded {len(rows)} products")
    
    def load_stores(self, csv_path: str):
        """Load stores CSV."""
        logger.info(f"Loading stores from {csv_path}")
        
        df = pd.read_csv(csv_path)
        logger.info(f"  Read {len(df)} stores")
        
        self.cursor.execute("TRUNCATE TABLE LANDING.STORES")
        
        insert_sql = """
        INSERT INTO LANDING.STORES (
            STORE_ID, STORE_NAME, STORE_TYPE, REGION, CITY, STATE, OPENED_DATE
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        rows = []
        for _, row in df.iterrows():
            rows.append((
                int(row['store_id']),
                str(row['store_name']),
                str(row['store_type']),
                str(row['region']),
                str(row['city']),
                str(row['state']),
                str(row['opened_date'])
            ))
        
        self.cursor.executemany(insert_sql, rows)
        self.conn.commit()
        logger.info(f"✅ Loaded {len(rows)} stores")
    
    def load_vendors(self, csv_path: str):
        """Load vendors CSV."""
        logger.info(f"Loading vendors from {csv_path}")
        
        df = pd.read_csv(csv_path)
        logger.info(f"  Read {len(df)} vendors")
        
        self.cursor.execute("TRUNCATE TABLE LANDING.VENDORS")
        
        insert_sql = """
        INSERT INTO LANDING.VENDORS (
            VENDOR_ID, VENDOR_NAME, VENDOR_COUNTRY, AVG_LEAD_TIME_DAYS, RELIABILITY_SCORE
        ) VALUES (%s, %s, %s, %s, %s)
        """
        
        rows = []
        for _, row in df.iterrows():
            rows.append((
                int(row['vendor_id']),
                str(row['vendor_name']),
                str(row['vendor_country']),
                int(row['avg_lead_time_days']),
                float(row['reliability_score'])
            ))
        
        self.cursor.executemany(insert_sql, rows)
        self.conn.commit()
        logger.info(f"✅ Loaded {len(rows)} vendors")
    
    def load_sales(self, csv_path: str):
        """Load sales CSV in batches."""
        logger.info(f"Loading sales from {csv_path}")
        
        df = pd.read_csv(csv_path)
        logger.info(f"  Read {len(df)} transactions")
        
        self.cursor.execute("TRUNCATE TABLE LANDING.SALES")
        
        insert_sql = """
        INSERT INTO LANDING.SALES (
            TRANSACTION_ID, SALE_DATE, PRODUCT_ID, STORE_ID, CUSTOMER_SEGMENT,
            QUANTITY_SOLD, UNIT_PRICE, DISCOUNT_AMOUNT, TOTAL_REVENUE, 
            COST_OF_GOODS, PROFIT
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Process in batches of 1000
        batch_size = 1000
        total_rows = len(df)
        
        for i in range(0, total_rows, batch_size):
            batch = df.iloc[i:i+batch_size]
            rows = []
            
            for _, row in batch.iterrows():
                rows.append((
                    int(row['transaction_id']),
                    str(row['sale_date']),
                    int(row['product_id']),
                    int(row['store_id']),
                    str(row['customer_segment']),
                    int(row['quantity_sold']),
                    float(row['unit_price']),
                    float(row['discount_amount']),
                    float(row['total_revenue']),
                    float(row['cost_of_goods']),
                    float(row['profit'])
                ))
            
            self.cursor.executemany(insert_sql, rows)
            self.conn.commit()
            logger.info(f"  Loaded batch {i//batch_size + 1}/{(total_rows + batch_size - 1)//batch_size} ({len(rows)} rows)")
        
        logger.info(f"✅ Loaded {total_rows} sales transactions")
    
    def load_inventory(self, csv_path: str):
        """Load inventory snapshot CSV."""
        logger.info(f"Loading inventory from {csv_path}")
        
        df = pd.read_csv(csv_path)
        logger.info(f"  Read {len(df)} inventory records")
        
        self.cursor.execute("TRUNCATE TABLE LANDING.INVENTORY_SNAPSHOT")
        
        insert_sql = """
        INSERT INTO LANDING.INVENTORY_SNAPSHOT (
            SNAPSHOT_DATE, PRODUCT_ID, STORE_ID, UNITS_ON_HAND, UNITS_ON_ORDER,
            REORDER_POINT, SAFETY_STOCK, DAYS_OF_SUPPLY
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Process in batches
        batch_size = 1000
        total_rows = len(df)
        
        for i in range(0, total_rows, batch_size):
            batch = df.iloc[i:i+batch_size]
            rows = []
            
            for _, row in batch.iterrows():
                rows.append((
                    str(row['snapshot_date']),
                    int(row['product_id']),
                    int(row['store_id']),
                    int(row['units_on_hand']),
                    int(row['units_on_order']),
                    int(row['reorder_point']),
                    int(row['safety_stock']),
                    float(row['days_of_supply'])
                ))
            
            self.cursor.executemany(insert_sql, rows)
            self.conn.commit()
        
        logger.info(f"✅ Loaded {total_rows} inventory records")
    
    def validate_load(self):
        """Validate loaded data."""
        logger.info("\n=== Data Validation ===")
        
        tables = {
            'PRODUCTS': 'LANDING.PRODUCTS',
            'STORES': 'LANDING.STORES',
            'VENDORS': 'LANDING.VENDORS',
            'SALES': 'LANDING.SALES',
            'INVENTORY': 'LANDING.INVENTORY_SNAPSHOT'
        }
        
        for name, table in tables.items():
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = self.cursor.fetchone()[0]
            logger.info(f"  {name}: {count:,} rows")
        
        # Sales summary
        logger.info("\n=== Sales Summary ===")
        self.cursor.execute("""
            SELECT 
                COUNT(*) as transactions,
                SUM(TOTAL_REVENUE) as total_revenue,
                SUM(PROFIT) as total_profit,
                AVG(TOTAL_REVENUE) as avg_transaction
            FROM LANDING.SALES
        """)
        result = self.cursor.fetchone()
        logger.info(f"  Transactions: {result[0]:,}")
        logger.info(f"  Total Revenue: ${result[1]:,.2f}")
        logger.info(f"  Total Profit: ${result[2]:,.2f}")
        logger.info(f"  Avg Transaction: ${result[3]:.2f}")


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description='Load supply chain data into Snowflake (certificate-safe)'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data/raw',
        help='Directory containing CSV files'
    )
    
    args = parser.parse_args()
    
    data_path = Path(args.data_dir)
    
    loader = SimpleSnowflakeLoader()
    
    try:
        logger.info("🚀 Starting data load...")
        
        # Connect
        loader.connect()
        
        # Load each file
        if (data_path / 'products.csv').exists():
            loader.load_products(str(data_path / 'products.csv'))
        
        if (data_path / 'stores.csv').exists():
            loader.load_stores(str(data_path / 'stores.csv'))
        
        if (data_path / 'vendors.csv').exists():
            loader.load_vendors(str(data_path / 'vendors.csv'))
        
        if (data_path / 'sales.csv').exists():
            loader.load_sales(str(data_path / 'sales.csv'))
        
        if (data_path / 'inventory_snapshot.csv').exists():
            loader.load_inventory(str(data_path / 'inventory_snapshot.csv'))
        
        # Validate
        loader.validate_load()
        
        logger.info("\n✅ ✅ ✅ DATA LOAD COMPLETED SUCCESSFULLY! ✅ ✅ ✅")
        
    except Exception as e:
        logger.error(f"\n❌ Data load failed: {e}")
        raise
    
    finally:
        loader.disconnect()


if __name__ == "__main__":
    main()
