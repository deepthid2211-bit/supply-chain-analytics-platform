"""
Supply Chain Data Loader for Snowflake
=======================================

Loads generated supply chain CSV files into Snowflake data warehouse.
Creates schemas and landing tables if they don't exist.

Author: Deepthi Desharaju
Date: February 2026
"""

import snowflake.connector
import pandas as pd
import yaml
import logging
from pathlib import Path
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SupplyChainLoader:
    """
    Loads supply chain data into Snowflake.
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
            raise FileNotFoundError(
                f"Config file not found: {config_path}\n"
                f"Copy config/config.template.yaml to config/config.yaml"
            )
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        return config['snowflake']
    
    def connect(self):
        """Establish connection to Snowflake."""
        try:
            self.conn = snowflake.connector.connect(
                user=self.config['user'],
                password=self.config['password'],
                account=self.config['account'],
                warehouse=self.config['warehouse'],
                database=self.config['database'],
                schema=self.config['schema']
            )
            self.cursor = self.conn.cursor()
            logger.info(f"✅ Connected to Snowflake account: {self.config['account']}")
            logger.info(f"   Database: {self.config['database']}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Snowflake: {e}")
            raise
    
    def disconnect(self):
        """Close Snowflake connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Disconnected from Snowflake")
    
    def create_schemas_and_tables(self):
        """Create database schemas and landing tables."""
        logger.info("Setting up database schemas and tables...")
        
        # Create schemas
        logger.info("Creating schemas...")
        self.cursor.execute("CREATE SCHEMA IF NOT EXISTS LANDING")
        self.cursor.execute("CREATE SCHEMA IF NOT EXISTS STAGING")
        self.cursor.execute("CREATE SCHEMA IF NOT EXISTS MARTS")
        logger.info("✅ Schemas created/verified: LANDING, STAGING, MARTS")
        
        # Create landing tables
        logger.info("Creating landing tables...")
        
        # Products table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS LANDING.PRODUCTS (
            PRODUCT_ID INT PRIMARY KEY,
            SKU VARCHAR(50) UNIQUE,
            PRODUCT_NAME VARCHAR(200),
            CATEGORY VARCHAR(50),
            SUBCATEGORY VARCHAR(50),
            BRAND VARCHAR(100),
            UNIT_COST DECIMAL(10,2),
            UNIT_PRICE DECIMAL(10,2),
            SUPPLIER VARCHAR(100),
            LOADED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """)
        logger.info("✅ Created: LANDING.PRODUCTS")
        
        # Stores table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS LANDING.STORES (
            STORE_ID INT PRIMARY KEY,
            STORE_NAME VARCHAR(100),
            STORE_TYPE VARCHAR(50),
            REGION VARCHAR(50),
            CITY VARCHAR(100),
            STATE VARCHAR(2),
            OPENED_DATE DATE,
            LOADED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """)
        logger.info("✅ Created: LANDING.STORES")
        
        # Vendors table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS LANDING.VENDORS (
            VENDOR_ID INT PRIMARY KEY,
            VENDOR_NAME VARCHAR(200),
            VENDOR_COUNTRY VARCHAR(50),
            AVG_LEAD_TIME_DAYS INT,
            RELIABILITY_SCORE DECIMAL(5,2),
            LOADED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """)
        logger.info("✅ Created: LANDING.VENDORS")
        
        # Sales table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS LANDING.SALES (
            TRANSACTION_ID INT PRIMARY KEY,
            SALE_DATE DATE,
            PRODUCT_ID INT,
            STORE_ID INT,
            CUSTOMER_SEGMENT VARCHAR(50),
            QUANTITY_SOLD INT,
            UNIT_PRICE DECIMAL(10,2),
            DISCOUNT_AMOUNT DECIMAL(10,2),
            TOTAL_REVENUE DECIMAL(10,2),
            COST_OF_GOODS DECIMAL(10,2),
            PROFIT DECIMAL(10,2),
            LOADED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """)
        logger.info("✅ Created: LANDING.SALES")
        
        # Inventory table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS LANDING.INVENTORY_SNAPSHOT (
            SNAPSHOT_DATE DATE,
            PRODUCT_ID INT,
            STORE_ID INT,
            UNITS_ON_HAND INT,
            UNITS_ON_ORDER INT,
            REORDER_POINT INT,
            SAFETY_STOCK INT,
            DAYS_OF_SUPPLY DECIMAL(5,1),
            LOADED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (SNAPSHOT_DATE, PRODUCT_ID, STORE_ID)
        )
        """)
        logger.info("✅ Created: LANDING.INVENTORY_SNAPSHOT")
        
        self.conn.commit()
        logger.info("✅ All tables created successfully")
    
    def load_csv(self, csv_path: str, table_name: str, mode: str = "append"):
        """
        Load CSV into Snowflake table.
        
        Args:
            csv_path: Path to CSV file
            table_name: Snowflake table name (schema.table)
            mode: 'append' or 'replace'
        """
        logger.info(f"Loading {csv_path} → {table_name}")
        
        # Read CSV
        df = pd.read_csv(csv_path)
        logger.info(f"  Read {len(df):,} records from CSV")
        
        # Clean column names (uppercase for Snowflake)
        df.columns = [col.upper() for col in df.columns]
        
        # Handle mode
        if mode == 'replace':
            logger.info(f"  Truncating table {table_name}")
            self.cursor.execute(f"TRUNCATE TABLE {table_name}")
        
        # Bulk load using write_pandas
        from snowflake.connector.pandas_tools import write_pandas
        
        schema, table = table_name.split('.')
        
        success, nchunks, nrows, _ = write_pandas(
            conn=self.conn,
            df=df,
            table_name=table,
            schema=schema,
            quote_identifiers=False
        )
        
        if success:
            logger.info(f"✅ Loaded {nrows:,} rows in {nchunks} chunks")
        else:
            logger.error(f"❌ Failed to load data")
            raise Exception("Data load failed")
        
        self.conn.commit()
    
    def load_all_files(self, data_dir: str = "data/raw", mode: str = "append"):
        """Load all CSV files from data directory."""
        data_path = Path(data_dir)
        
        # File to table mapping
        files_to_load = {
            'products.csv': 'LANDING.PRODUCTS',
            'stores.csv': 'LANDING.STORES',
            'vendors.csv': 'LANDING.VENDORS',
            'sales.csv': 'LANDING.SALES',
            'inventory_snapshot.csv': 'LANDING.INVENTORY_SNAPSHOT'
        }
        
        for filename, table_name in files_to_load.items():
            csv_file = data_path / filename
            if csv_file.exists():
                self.load_csv(str(csv_file), table_name, mode=mode)
            else:
                logger.warning(f"⚠️  File not found: {csv_file}")
    
    def validate_load(self):
        """Run validation checks on loaded data."""
        logger.info("\n=== Data Validation ===")
        
        tables = ['PRODUCTS', 'STORES', 'VENDORS', 'SALES', 'INVENTORY_SNAPSHOT']
        
        for table in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM LANDING.{table}")
            count = self.cursor.fetchone()[0]
            logger.info(f"  LANDING.{table}: {count:,} rows")
        
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
        
        # Product categories
        logger.info("\n=== Product Categories ===")
        self.cursor.execute("""
            SELECT CATEGORY, COUNT(*) as count
            FROM LANDING.PRODUCTS
            GROUP BY CATEGORY
            ORDER BY count DESC
        """)
        for row in self.cursor.fetchall():
            logger.info(f"  {row[0]}: {row[1]} products")


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description='Load supply chain data into Snowflake'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data/raw',
        help='Directory containing CSV files (default: data/raw)'
    )
    parser.add_argument(
        '--mode',
        type=str,
        choices=['append', 'replace'],
        default='replace',
        help='Load mode: append or replace (default: replace)'
    )
    parser.add_argument(
        '--skip-setup',
        action='store_true',
        help='Skip schema/table creation'
    )
    
    args = parser.parse_args()
    
    # Initialize loader
    loader = SupplyChainLoader()
    
    try:
        # Connect
        loader.connect()
        
        # Create schemas and tables
        if not args.skip_setup:
            loader.create_schemas_and_tables()
        
        # Load all CSV files
        loader.load_all_files(data_dir=args.data_dir, mode=args.mode)
        
        # Validate
        loader.validate_load()
        
        logger.info("\n✅ Data load completed successfully!")
        
    except Exception as e:
        logger.error(f"\n❌ Data load failed: {e}")
        raise
    
    finally:
        loader.disconnect()


if __name__ == "__main__":
    main()
