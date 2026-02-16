# Setup Guide - Vulnerability Analytics Platform

**Complete step-by-step instructions to build and run the project**

---

## 📋 Prerequisites

Before you begin, ensure you have:

- [ ] **Python 3.8+** installed ([Download](https://www.python.org/downloads/))
- [ ] **Git** installed ([Download](https://git-scm.com/downloads))
- [ ] **Snowflake account** (free trial: [signup.snowflake.com](https://signup.snowflake.com/))
- [ ] **Power BI Desktop** (free: [powerbi.microsoft.com](https://powerbi.microsoft.com/))
- [ ] **Code editor** (VS Code recommended)

---

## 🚀 Quick Start (30 minutes)

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/vulnerability-analytics-platform.git
cd vulnerability-analytics-platform
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Snowflake

1. **Copy config template:**
```bash
cp config/config.template.yaml config/config.yaml
```

2. **Edit `config/config.yaml` with your Snowflake credentials:**

```yaml
snowflake:
  account: "your_account.us-east-1"  # From Snowflake UI
  user: "YOUR_USERNAME"
  password: "YOUR_PASSWORD"
  warehouse: "COMPUTE_WH"
  database: "VULNERABILITY_ANALYTICS"
  schema: "LANDING"
  role: "ACCOUNTADMIN"
```

**How to find your Snowflake account identifier:**
- Log into Snowflake
- Look at URL: `https://[account_locator].[region].snowflakecomputing.com`
- Example: `ab12345.us-east-1`

### Step 4: Extract CVE Data from NIST

```bash
# Extract last 90 days of CVE data (recommended for testing)
python data_pipeline/extract/nist_nvd_extractor.py --days 90

# This will:
# - Call NIST NVD API
# - Extract ~5,000-10,000 CVE records
# - Save to data/raw/cve_data_YYYY-MM-DD_to_YYYY-MM-DD.csv
# - Take ~10-15 minutes (API rate limits)
```

**Optional: Get NIST API key for faster extraction**
1. Request free key: https://nvd.nist.gov/developers/request-an-api-key
2. Add to config.yaml:
```yaml
nist:
  api_key: "your-api-key-here"
```
3. Re-run extraction (10x faster)

### Step 5: Load Data to Snowflake

```bash
python data_pipeline/load/snowflake_loader.py \
  --csv-path data/raw/cve_data_*.csv

# This will:
# - Create LANDING, STAGING, MARTS schemas
# - Create CVE_RAW table
# - Load CSV data
# - Run validation checks
```

**Expected output:**
```
✅ Connected to Snowflake
✅ Schemas created/verified
✅ Landing table CVE_RAW created
✅ Loaded 8,547 rows
✅ Validation passed
```

### Step 6: Set Up dbt

1. **Create dbt profile:**
```bash
mkdir -p ~/.dbt
cat > ~/.dbt/profiles.yml <<EOF
vulnerability_analytics:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: your_account.region
      user: YOUR_USERNAME
      password: YOUR_PASSWORD
      role: ACCOUNTADMIN
      database: VULNERABILITY_ANALYTICS
      warehouse: COMPUTE_WH
      schema: MARTS
      threads: 4
EOF
```

2. **Test dbt connection:**
```bash
cd dbt_project
dbt debug

# Should see: "All checks passed!"
```

3. **Run dbt models:**
```bash
# Run all transformations
dbt run

# Run data quality tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve  # Opens in browser
```

**Expected output:**
```
Completed successfully
- 4 staging models
- 5 mart models (fact + dimensions)
- All tests passed
```

---

## 🔧 Detailed Setup (If You Hit Issues)

### Snowflake Setup (Manual)

If automated setup fails, run SQL manually:

1. **Log into Snowflake UI**
2. **Create database:**
```sql
CREATE DATABASE VULNERABILITY_ANALYTICS;
USE DATABASE VULNERABILITY_ANALYTICS;
```

3. **Create schemas:**
```sql
CREATE SCHEMA LANDING;
CREATE SCHEMA STAGING;
CREATE SCHEMA MARTS;
```

4. **Create landing table:**
```sql
CREATE TABLE LANDING.CVE_RAW (
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
```

5. **Load CSV via Snowflake UI:**
- Go to Databases → VULNERABILITY_ANALYTICS → LANDING → CVE_RAW
- Click "Load Data"
- Upload your CSV file
- Follow wizard

### Python Environment Issues

**Issue: `pip install` fails**
```bash
# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Try installing packages one by one
pip install pandas requests snowflake-connector-python
```

**Issue: Snowflake connector won't install**
```bash
# On Mac with M1/M2 chip:
brew install unixodbc
pip install snowflake-connector-python

# On Windows: Install Visual C++ Build Tools
# https://visualstudio.microsoft.com/downloads/
```

### NIST API Issues

**Issue: "Rate limit exceeded"**
- Wait 6 seconds between requests (script does this automatically)
- Get free API key for higher limits
- Reduce date range: `--days 30` instead of `--days 365`

**Issue: "No data returned"**
- Check internet connection
- Try: `curl https://services.nvd.nist.gov/rest/json/cves/2.0`
- NIST API may be down (rare), try again later

---

## 🎯 Next Steps After Setup

### Build Machine Learning Model

```bash
cd ml_model
python vulnerability_risk_model.py

# This will:
# - Query Snowflake for training data
# - Train Random Forest model
# - Save trained model
# - Generate predictions
# - Update fact table with ML scores
```

### Create Power BI Dashboard

1. **Open Power BI Desktop**
2. **Connect to Snowflake:**
   - Get Data → Snowflake
   - Server: `your_account.region.snowflakecomputing.com`
   - Warehouse: `COMPUTE_WH`
   - Database: `VULNERABILITY_ANALYTICS`
   - Schema: `MARTS`

3. **Import tables:**
   - FACT_VULNERABILITIES
   - DIM_PRODUCTS
   - DIM_VENDORS
   - DIM_VULNERABILITY_TYPES
   - DIM_DATE

4. **Create relationships:**
   - fact_vulnerabilities[product_key] → dim_products[product_key]
   - fact_vulnerabilities[vendor_key] → dim_vendors[vendor_key]
   - fact_vulnerabilities[vulnerability_type_key] → dim_vulnerability_types[vulnerability_type_key]

5. **Build visualizations:**
   - Refer to `docs/dashboard_design.md` for layout

### Publish to GitHub

```bash
# Initialize Git
git init
git add .
git commit -m "Initial commit - Vulnerability Analytics Platform"

# Create repo on GitHub, then:
git remote add origin https://github.com/yourusername/vulnerability-analytics-platform.git
git push -u origin main
```

**Remember:** Don't commit sensitive files (already in .gitignore)

---

## 🐛 Troubleshooting

### Common Errors

**Error: "Connection refused" (Snowflake)**
- Check account identifier format
- Verify credentials in config.yaml
- Test with: `python -c "import snowflake.connector; print('OK')"`

**Error: "Table already exists"**
- Use `--mode replace` to overwrite:
  ```bash
  python data_pipeline/load/snowflake_loader.py --csv-path data/raw/*.csv --mode replace
  ```

**Error: dbt "Could not find profile"**
- Check `~/.dbt/profiles.yml` exists
- Verify YAML indentation (spaces, not tabs)

**Error: "Module not found"**
- Ensure virtual environment is activated: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`

---

## 📚 Additional Resources

- **NIST NVD API Docs:** https://nvd.nist.gov/developers
- **Snowflake Free Trial:** https://signup.snowflake.com/
- **dbt Documentation:** https://docs.getdbt.com/
- **Power BI Learning:** https://learn.microsoft.com/power-bi/

---

## ✅ Validation Checklist

Before showcasing your project, verify:

- [ ] Python code runs without errors
- [ ] Snowflake tables populated with data
- [ ] dbt models run successfully (`dbt run`)
- [ ] Data quality tests pass (`dbt test`)
- [ ] ML model trains and generates predictions
- [ ] Power BI dashboard connects and displays data
- [ ] GitHub repo has clear README
- [ ] All sensitive data removed from Git

---

**Need help?** Open an issue on GitHub or contact deepthi: desharajudeepthi@gmail.com
