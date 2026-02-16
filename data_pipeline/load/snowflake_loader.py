"""
Snowflake Data Loader
=====================

Loads extracted CVE data from CSV into Snowflake data warehouse.
Creates schemas and tables if they don't exist.

Author: Deepthi Desharaju
Date: February 2026
"""

import snowflake.connector
import pandas as pd
import yaml
import logging
from pathlib import Path
from typing import Optional
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SnowflakeLoader:
    """
    Loads data into Snowflake data warehouse.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize Snowflake connection.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config = self._load_config(config_path)
        self.conn = None
        self.cursor = None
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(
                f"Config file not found: {config_path}\n"
                f"Copy config/config.template.yaml to config/config.yaml and update with your credentials"
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
            logger.info("Connected to Snowflake successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {e}")
            raise
    
    def disconnect(self):
        """Close Snowflake connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Disconnected from Snowflake")
    
    def create_schema_and_tables(self):
        """
        Create database schemas and landing tables if they don't exist.
        """
        logger.info("Setting up database schemas and tables...")
        
        # Create schemas
        schemas_sql = """
        -- Landing zone for raw data
        CREATE SCHEMA IF NOT EXISTS LANDING;
        
        -- Staging zone for cleansed data
        CREATE SCHEMA IF NOT EXISTS STAGING;
        
        -- Analytics marts (dimensional models)
        CREATE SCHEMA IF NOT EXISTS MARTS;
        """
        
        self.cursor.execute(schemas_sql)
        logger.info("Schemas created/verified")
        
        # Create landing table for raw CVE data
        landing_table_sql = """
        CREATE TABLE IF NOT EXISTS LANDING.CVE_RAW (
            CVE_ID VARCHAR(50) PRIMARY KEY,
            PUBLISHED_DATE TIMESTAMP_NTZ,
            MODIFIED_DATE TIMESTAMP_NTZ,
            VULN_STATUS VARCHAR(50),
            DESCRIPTION VARCHAR(5000),
            CVSS_V3_SCORE DECIMAL(3,1),
            CVSS_V3_SEVERITY VARCHAR(20),
            ATTACK_VECTOR VARCHAR(20),
            ATTACK_COMPLEXITY VARCHAR(20),
            PRIVILEGES_REQUIRED VARCHAR(20),
            USER_INTERACTION VARCHAR(20),
            EXPLOITABILITY_SCORE DECIMAL(3,1),
            IMPACT_SCORE DECIMAL(3,1),
            CWE_ID VARCHAR(200),
            VENDOR VARCHAR(200),
            PRODUCT VARCHAR(500),
            REFERENCE_COUNT INT,
            EXTRACTED_AT TIMESTAMP_NTZ,
            LOADED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        );
        """
        
        self.cursor.execute(landing_table_sql)
        logger.info("Landing table CVE_RAW created/verified")
        
        self.conn.commit()
    
    def load_csv_to_snowflake(
        self, 
        csv_path: str,
        table_name: str = "LANDING.CVE_RAW",
        mode: str = "append"
    ):
        """
        Load CSV data into Snowflake table.
        
        Args:
            csv_path: Path to CSV file
            table_name: Snowflake table name (schema.table)
            mode: 'append' or 'replace'
        """
        logger.info(f"Loading data from {csv_path} to {table_name}")
        
        # Read CSV
        df = pd.read_csv(csv_path)
        logger.info(f"Read {len(df)} records from CSV")
        
        # Clean column names for Snowflake (uppercase)
        df.columns = [col.upper() for col in df.columns]
        
        # Handle mode
        if mode == 'replace':
            logger.info(f"Truncating table {table_name}")
            self.cursor.execute(f"TRUNCATE TABLE {table_name}")
        
        # Insert data using Snowflake's write_pandas (efficient bulk load)
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
            logger.info(f"Successfully loaded {nrows} rows in {nchunks} chunks")
        else:
            logger.error("Failed to load data")
            raise Exception("Data load failed")
        
        self.conn.commit()
    
    def validate_load(self, table_name: str = "LANDING.CVE_RAW"):
        """
        Validate data load by running basic checks.
        
        Args:
            table_name: Table to validate
        """
        logger.info(f"\n=== Validating {table_name} ===")
        
        # Row count
        self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = self.cursor.fetchone()[0]
        logger.info(f"Total rows: {row_count:,}")
        
        # Severity distribution
        self.cursor.execute(f"""
            SELECT CVSS_V3_SEVERITY, COUNT(*) as count
            FROM {table_name}
            WHERE CVSS_V3_SEVERITY IS NOT NULL
            GROUP BY CVSS_V3_SEVERITY
            ORDER BY count DESC
        """)
        
        logger.info("\nSeverity Distribution:")
        for row in self.cursor.fetchall():
            logger.info(f"  {row[0]}: {row[1]:,}")
        
        # Date range
        self.cursor.execute(f"""
            SELECT 
                MIN(PUBLISHED_DATE) as earliest,
                MAX(PUBLISHED_DATE) as latest
            FROM {table_name}
        """)
        
        date_range = self.cursor.fetchone()
        logger.info(f"\nDate Range: {date_range[0]} to {date_range[1]}")
        
        # Data quality checks
        self.cursor.execute(f"""
            SELECT 
                COUNT(*) as total_rows,
                COUNT(CVE_ID) as cve_ids,
                COUNT(CVSS_V3_SCORE) as cvss_scores,
                COUNT(VENDOR) as vendors,
                COUNT(PRODUCT) as products
            FROM {table_name}
        """)
        
        quality_check = self.cursor.fetchone()
        logger.info("\nData Quality:")
        logger.info(f"  Total rows: {quality_check[0]:,}")
        logger.info(f"  CVE IDs (PK): {quality_check[1]:,}")
        logger.info(f"  CVSS Scores: {quality_check[2]:,}")
        logger.info(f"  Vendors: {quality_check[3]:,}")
        logger.info(f"  Products: {quality_check[4]:,}")


def main():
    """
    Main execution function.
    """
    parser = argparse.ArgumentParser(
        description='Load CVE data into Snowflake'
    )
    parser.add_argument(
        '--csv-path',
        type=str,
        required=True,
        help='Path to CSV file to load'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to Snowflake config file (default: config/config.yaml)'
    )
    parser.add_argument(
        '--mode',
        type=str,
        choices=['append', 'replace'],
        default='append',
        help='Load mode: append or replace (default: append)'
    )
    parser.add_argument(
        '--skip-setup',
        action='store_true',
        help='Skip schema and table creation (if already exists)'
    )
    
    args = parser.parse_args()
    
    # Initialize loader
    loader = SnowflakeLoader(config_path=args.config)
    
    try:
        # Connect
        loader.connect()
        
        # Create schemas and tables (unless skipped)
        if not args.skip_setup:
            loader.create_schema_and_tables()
        
        # Load data
        loader.load_csv_to_snowflake(
            csv_path=args.csv_path,
            mode=args.mode
        )
        
        # Validate
        loader.validate_load()
        
        logger.info("\n✅ Data load completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Data load failed: {e}")
        raise
    
    finally:
        loader.disconnect()


if __name__ == "__main__":
    main()
