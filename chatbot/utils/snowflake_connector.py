"""
Snowflake connector for executing queries and retrieving data
"""

import snowflake.connector
import pandas as pd
from typing import Optional, Dict, Any


class SnowflakeConnector:
    """Handle Snowflake connections and query execution"""
    
    def __init__(self, account: str, user: str, password: str, 
                 database: str, schema: str, warehouse: str = "COMPUTE_WH"):
        """Initialize Snowflake connection"""
        self.connection_params = {
            "account": account,
            "user": user,
            "password": password,
            "database": database,
            "schema": schema,
            "warehouse": warehouse
        }
        self.conn = None
        self.connect()
    
    def connect(self) -> None:
        """Establish connection to Snowflake"""
        try:
            self.conn = snowflake.connector.connect(**self.connection_params)
        except Exception as e:
            raise Exception(f"Failed to connect to Snowflake: {str(e)}")
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute SQL query and return results as DataFrame"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            
            # Fetch results
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            # Convert to DataFrame
            df = pd.DataFrame(results, columns=columns)
            cursor.close()
            
            return df
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get information about available tables and columns"""
        try:
            # Get tables
            tables_query = f"""
            SELECT TABLE_NAME, TABLE_TYPE
            FROM {self.connection_params['database']}.INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = '{self.connection_params['schema']}'
            ORDER BY TABLE_NAME
            """
            tables_df = self.execute_query(tables_query)
            
            # Get columns for each table
            schema_info = {}
            for table_name in tables_df['TABLE_NAME']:
                columns_query = f"""
                SELECT COLUMN_NAME, DATA_TYPE
                FROM {self.connection_params['database']}.INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = '{self.connection_params['schema']}'
                AND TABLE_NAME = '{table_name}'
                ORDER BY ORDINAL_POSITION
                """
                columns_df = self.execute_query(columns_query)
                schema_info[table_name] = columns_df.to_dict('records')
            
            return schema_info
        except Exception as e:
            raise Exception(f"Failed to retrieve schema info: {str(e)}")
    
    def get_table_preview(self, table_name: str, limit: int = 5) -> pd.DataFrame:
        """Get preview of table data"""
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return self.execute_query(query)
    
    def close(self) -> None:
        """Close Snowflake connection"""
        if self.conn:
            self.conn.close()
