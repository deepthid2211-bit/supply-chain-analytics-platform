"""
Demand Forecasting Model
========================

Time series forecasting for inventory optimization.
Predicts future demand by product/store to prevent stockouts.

Author: Deepthi Desharaju
Date: February 2026
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import snowflake.connector
import yaml
import logging
import joblib
from pathlib import Path
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DemandForecaster:
    """
    Demand forecasting using Random Forest.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize forecaster."""
        self.config = self._load_config(config_path)
        self.model = None
        self.feature_importance = None
    
    def _load_config(self, config_path: str) -> dict:
        """Load Snowflake config."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config['snowflake']
    
    def connect_snowflake(self):
        """Connect to Snowflake."""
        return snowflake.connector.connect(
            user=self.config['user'],
            password=self.config['password'],
            account=self.config['account'],
            warehouse=self.config['warehouse'],
            database=self.config['database'],
            schema='MARTS',
            insecure_mode=True
        )
    
    def extract_features(self):
        """
        Extract features for demand forecasting from Snowflake.
        """
        logger.info("Extracting training data from Snowflake...")
        
        conn = self.connect_snowflake()
        
        query = """
        SELECT 
            s.PRODUCT_KEY,
            s.STORE_KEY,
            s.SALE_DATE,
            SUM(s.QUANTITY_SOLD) as total_quantity,
            SUM(s.TOTAL_REVENUE) as total_revenue,
            COUNT(*) as transaction_count,
            AVG(s.UNIT_PRICE) as avg_price,
            SUM(s.DISCOUNT_AMOUNT) as total_discount,
            -- Product attributes
            p.CATEGORY,
            p.SUBCATEGORY,
            p.BRAND,
            p.UNIT_COST,
            -- Store attributes
            st.STORE_TYPE,
            st.REGION,
            -- Date attributes
            d.MONTH,
            d.QUARTER,
            d.DAY_OF_WEEK,
            d.IS_WEEKEND,
            d.IS_HOLIDAY_SEASON
        FROM MARTS_MARTS.FACT_SALES s
        JOIN MARTS_MARTS.DIM_PRODUCTS p ON s.PRODUCT_KEY = p.PRODUCT_KEY
        JOIN MARTS_MARTS.DIM_STORES st ON s.STORE_KEY = st.STORE_KEY
        JOIN MARTS_MARTS.DIM_DATE d ON s.DATE_KEY = d.DATE_KEY
        GROUP BY 
            s.PRODUCT_KEY, s.STORE_KEY, s.SALE_DATE,
            p.CATEGORY, p.SUBCATEGORY, p.BRAND, p.UNIT_COST,
            st.STORE_TYPE, st.REGION,
            d.MONTH, d.QUARTER, d.DAY_OF_WEEK, d.IS_WEEKEND, d.IS_HOLIDAY_SEASON
        ORDER BY s.SALE_DATE
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        logger.info(f"Extracted {len(df)} records for training")
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create additional features for forecasting.
        """
        logger.info("Engineering features...")
        
        # Convert date
        df['SALE_DATE'] = pd.to_datetime(df['SALE_DATE'])
        
        # Lag features (previous day's demand)
        df = df.sort_values(['PRODUCT_KEY', 'STORE_KEY', 'SALE_DATE'])
        df['lag_1_day_quantity'] = df.groupby(['PRODUCT_KEY', 'STORE_KEY'])['TOTAL_QUANTITY'].shift(1)
        df['lag_7_day_quantity'] = df.groupby(['PRODUCT_KEY', 'STORE_KEY'])['TOTAL_QUANTITY'].shift(7)
        
        # Rolling averages
        df['rolling_7_day_avg'] = df.groupby(['PRODUCT_KEY', 'STORE_KEY'])['TOTAL_QUANTITY'].transform(
            lambda x: x.rolling(window=7, min_periods=1).mean()
        )
        df['rolling_30_day_avg'] = df.groupby(['PRODUCT_KEY', 'STORE_KEY'])['TOTAL_QUANTITY'].transform(
            lambda x: x.rolling(window=30, min_periods=1).mean()
        )
        
        # Fill NaN values
        df = df.fillna(0)
        
        # Encode categorical variables
        df['CATEGORY_encoded'] = pd.Categorical(df['CATEGORY']).codes
        df['SUBCATEGORY_encoded'] = pd.Categorical(df['SUBCATEGORY']).codes
        df['BRAND_encoded'] = pd.Categorical(df['BRAND']).codes
        df['STORE_TYPE_encoded'] = pd.Categorical(df['STORE_TYPE']).codes
        df['REGION_encoded'] = pd.Categorical(df['REGION']).codes
        
        logger.info("Feature engineering complete")
        return df
    
    def train_model(self, df: pd.DataFrame):
        """
        Train Random Forest model for demand forecasting.
        """
        logger.info("Training demand forecasting model...")
        
        # Features for training
        feature_cols = [
            'PRODUCT_KEY', 'STORE_KEY',
            'MONTH', 'QUARTER', 'DAY_OF_WEEK', 'IS_WEEKEND', 'IS_HOLIDAY_SEASON',
            'AVG_PRICE', 'TOTAL_DISCOUNT', 'UNIT_COST',
            'CATEGORY_encoded', 'SUBCATEGORY_encoded', 'BRAND_encoded',
            'STORE_TYPE_encoded', 'REGION_encoded',
            'lag_1_day_quantity', 'lag_7_day_quantity',
            'rolling_7_day_avg', 'rolling_30_day_avg'
        ]
        
        X = df[feature_cols]
        y = df['TOTAL_QUANTITY']
        
        # Train/test split (80/20)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train Random Forest
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        train_mae = mean_absolute_error(y_train, train_pred)
        test_mae = mean_absolute_error(y_test, test_pred)
        test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
        
        # Calculate MAPE (Mean Absolute Percentage Error)
        test_mape = np.mean(np.abs((y_test - test_pred) / np.maximum(y_test, 1))) * 100
        
        logger.info(f"\n=== Model Performance ===")
        logger.info(f"Train MAE: {train_mae:.2f}")
        logger.info(f"Test MAE: {test_mae:.2f}")
        logger.info(f"Test RMSE: {test_rmse:.2f}")
        logger.info(f"Test MAPE: {test_mape:.2f}%")
        
        # Feature importance
        self.feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info(f"\n=== Top 10 Important Features ===")
        logger.info(self.feature_importance.head(10).to_string())
        
        return {
            'train_mae': train_mae,
            'test_mae': test_mae,
            'test_rmse': test_rmse,
            'test_mape': test_mape
        }
    
    def save_model(self, path: str = "ml_model/demand_forecast_model.pkl"):
        """Save trained model."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)
        logger.info(f"Model saved to {path}")
    
    def generate_forecasts(self, days_ahead: int = 30):
        """
        Generate demand forecasts for next N days.
        """
        logger.info(f"Generating forecasts for next {days_ahead} days...")
        
        conn = self.connect_snowflake()
        
        # Get latest data for each product/store
        query = """
        SELECT DISTINCT
            PRODUCT_KEY,
            STORE_KEY
        FROM MARTS_MARTS.FACT_SALES
        """
        
        product_stores = pd.read_sql(query, conn)
        
        # Generate forecast dates
        today = datetime.now().date()
        forecast_dates = [today + timedelta(days=i) for i in range(1, days_ahead + 1)]
        
        forecasts = []
        
        for _, row in product_stores.iterrows():
            product_key = row['PRODUCT_KEY']
            store_key = row['STORE_KEY']
            
            for forecast_date in forecast_dates:
                # Create features for prediction
                # (In real implementation, would use actual historical data)
                forecast_row = {
                    'product_key': product_key,
                    'store_key': store_key,
                    'forecast_date': forecast_date,
                    'forecasted_quantity': np.random.randint(1, 10)  # Placeholder
                }
                forecasts.append(forecast_row)
        
        forecast_df = pd.DataFrame(forecasts)
        
        logger.info(f"Generated {len(forecast_df)} forecasts")
        
        conn.close()
        return forecast_df


def main():
    """Main execution."""
    logger.info("🚀 Starting Demand Forecasting Model Training...")
    
    forecaster = DemandForecaster()
    
    # Extract data
    df = forecaster.extract_features()
    
    # Engineer features
    df = forecaster.engineer_features(df)
    
    # Train model
    metrics = forecaster.train_model(df)
    
    # Save model
    forecaster.save_model()
    
    logger.info("\n✅ ✅ ✅ MODEL TRAINING COMPLETE! ✅ ✅ ✅")
    logger.info(f"\nModel Performance:")
    logger.info(f"  • Test MAE: {metrics['test_mae']:.2f} units")
    logger.info(f"  • Test RMSE: {metrics['test_rmse']:.2f} units")
    logger.info(f"  • Test MAPE: {metrics['test_mape']:.1f}%")
    
    logger.info("\n🎯 Model ready for deployment!")


if __name__ == "__main__":
    main()
