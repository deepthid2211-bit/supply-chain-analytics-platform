# dbt Supply Chain Analytics

**dbt models for dimensional data warehouse**

## Project Structure

```
models/
├── staging/              # Raw → Cleansed
│   ├── sources.yml       # Source definitions
│   ├── stg_products.sql
│   └── stg_sales.sql
│
└── marts/                # Dimensional models
    ├── schema.yml        # Model docs + tests
    ├── dim_products.sql  # Product dimension
    ├── dim_stores.sql    # Store dimension
    ├── dim_date.sql      # Date dimension
    └── fact_sales.sql    # Sales fact table
```

## Data Model

**Star Schema:**

```
       fact_sales
           |
    ┌──────┼──────┐
    │      │      │
dim_products  dim_stores  dim_date
```

### Fact Table: fact_sales
- **Grain:** One row per transaction
- **Measures:** quantity_sold, total_revenue, profit, etc.
- **Keys:** product_key, store_key, date_key

### Dimensions:
- **dim_products:** Product catalog with category, brand, pricing
- **dim_stores:** Store locations with type, region
- **dim_date:** Date attributes (year, quarter, month, weekend flags, etc.)

## Running dbt

```bash
# Test connection
dbt debug

# Run all models
dbt run

# Run data quality tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve
```

## Models Built

✅ 2 staging models  
✅ 3 dimension models  
✅ 1 fact model  
✅ Data quality tests  

**Total:** 6 dbt models ready to run!
