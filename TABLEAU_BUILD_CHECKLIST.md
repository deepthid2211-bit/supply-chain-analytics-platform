# ✅ Tableau Build Progress Checklist

**Track your dashboard building progress!**

---

## 📥 Phase 1: Setup (10-15 min)

- [ ] Downloaded Tableau Public from https://public.tableau.com/app/discover
- [ ] Installed Tableau Public
- [ ] Opened application successfully
- [ ] Created Tableau Public account (deepthid2211@gmail.com)

---

## 🔗 Phase 2: Data Connection (10 min)

- [ ] Clicked "Connect to Data" in Tableau
- [ ] Selected "Snowflake" connector
- [ ] Entered server: `VYUVIGG-RVB11850.snowflakecomputing.com`
- [ ] Entered credentials (Username: Deepthi)
- [ ] Selected Warehouse: COMPUTE_WH
- [ ] Selected Database: SUPPLY_CHAIN_ANALYTICS
- [ ] Selected Schema: MARTS_MARTS
- [ ] Dragged FACT_SALES to canvas
- [ ] Joined DIM_PRODUCTS (auto-join on PRODUCT_KEY)
- [ ] Joined DIM_STORES (auto-join on STORE_KEY)
- [ ] Joined DIM_DATE (auto-join on DATE_KEY)
- [ ] Clicked "Sheet 1" to start building

**✅ Connection successful when you see data in "Data" pane!**

---

## 📊 Phase 3: Build Executive Dashboard (45-60 min)

### KPI Cards (15 min)

- [ ] **Revenue Card:**
  - [ ] Created new sheet (name: "Revenue KPI")
  - [ ] Dragged `Total Revenue` to Text
  - [ ] Formatted as Currency
  - [ ] Set font size to 48pt
  - [ ] Added title "Total Revenue"

- [ ] **Profit Card:**
  - [ ] Created new sheet (name: "Profit KPI")
  - [ ] Dragged `Profit` to Text
  - [ ] Formatted as Currency  
  - [ ] Set font size to 48pt
  - [ ] Added title "Total Profit"

- [ ] **Transaction Count Card:**
  - [ ] Created new sheet (name: "Transaction Count")
  - [ ] Dragged `Sales Key` to Text
  - [ ] Changed to COUNT(DISTINCT)
  - [ ] Set font size to 48pt
  - [ ] Added title "Total Transactions"

- [ ] **Avg Transaction Card:**
  - [ ] Created calculated field "Avg Transaction"
    - Formula: `SUM([Total Revenue]) / COUNTD([Sales Key])`
  - [ ] Dragged to Text
  - [ ] Formatted as Currency
  - [ ] Set font size to 48pt

### Charts (30 min)

- [ ] **Revenue Trend Line:**
  - [ ] Created new sheet (name: "Revenue Trend")
  - [ ] Dragged `Sale Date` to Columns
  - [ ] Changed to Month view
  - [ ] Dragged `Total Revenue` to Rows
  - [ ] Dragged `Category` to Color
  - [ ] Added trend line
  - [ ] Added proper title

- [ ] **Category Bar Chart:**
  - [ ] Created new sheet (name: "Sales by Category")
  - [ ] Dragged `Category` to Rows
  - [ ] Dragged `Total Revenue` to Columns
  - [ ] Sorted descending
  - [ ] Added color gradient
  - [ ] Enabled data labels

- [ ] **Top 10 Products Table:**
  - [ ] Created new sheet (name: "Top Products")
  - [ ] Dragged `Product Name` to Rows
  - [ ] Dragged `Quantity Sold`, `Total Revenue`, `Profit` to Columns
  - [ ] Added filter: Top 10 by Revenue
  - [ ] Formatted numbers (currency, whole numbers)

### Dashboard Assembly (15 min)

- [ ] Created new Dashboard (name: "Executive Overview")
- [ ] Set size: 1600 x 900 or Automatic
- [ ] Dragged all KPI cards to top row (horizontal)
- [ ] Dragged Revenue Trend below KPIs (full width)
- [ ] Dragged Category chart and Product table side-by-side at bottom
- [ ] Added dashboard title: "Supply Chain Analytics - Executive Overview"
- [ ] Added filters (optional):
  - [ ] Date range slider
  - [ ] Category dropdown
- [ ] Adjusted spacing and alignment
- [ ] Made it look clean and professional

---

## 📸 Phase 4: Screenshots (10 min)

- [ ] Opened Executive Dashboard in Tableau
- [ ] Took full dashboard screenshot
  - Mac: Cmd + Shift + 4
  - Windows: Win + Shift + S
- [ ] Saved as: `dashboards/screenshots/executive_tableau.png`
- [ ] Verified screenshot is clear and readable
- [ ] (Optional) Took additional detail shots of specific charts

---

## 🌐 Phase 5: Publish to Tableau Public (10 min)

- [ ] Clicked File → Save to Tableau Public As...
- [ ] Signed in to Tableau Public account
- [ ] Entered workbook details:
  - [ ] Name: "Supply Chain Analytics Platform"
  - [ ] Description: "Supply chain analytics with Snowflake, dbt, and ML"
  - [ ] Tags: supply-chain, analytics, snowflake, dbt, data-engineering
- [ ] Clicked Save (uploads to cloud)
- [ ] **COPIED PUBLIC LINK** (save this!)
  - Format: `https://public.tableau.com/profile/[username]/viz/[workbook]`
- [ ] Opened link in browser to verify it works
- [ ] Tested interactivity (filters, hover tooltips)

**✅ Link to save:** _______________________________________________

---

## 📝 Phase 6: Update Documentation (10 min)

- [ ] Updated README.md with Tableau section:
  ```markdown
  ## 📊 Interactive Dashboards
  
  **Live Dashboard:** [View on Tableau Public](YOUR_LINK_HERE)
  
  ![Executive Dashboard](dashboards/screenshots/executive_tableau.png)
  ```

- [ ] Added Tableau Public link to portfolio notes

---

## 🎯 Optional: Additional Dashboards (If Time Permits)

### Dashboard 2: Product & Store Analysis (30 min)

- [ ] Store Type Pie Chart
- [ ] Regional Heatmap
- [ ] Product/Store Performance Matrix
- [ ] Published & screenshot taken

### Dashboard 3: Time Intelligence (30 min)

- [ ] Monthly MoM Growth chart
- [ ] Weekday vs Weekend comparison
- [ ] Holiday season impact
- [ ] Published & screenshot taken

---

## ✅ Final Verification

- [ ] All screenshots saved in `dashboards/screenshots/`
- [ ] Tableau Public link works when opened in browser
- [ ] README.md updated with Tableau section
- [ ] Ready to push to GitHub!

---

## 🎊 Completion Status

**Started:** ___:___ PST  
**Finished:** ___:___ PST  
**Total Time:** ____ hours  

**Dashboards Built:** 
- [ ] Executive Overview (minimum required)
- [ ] Product & Store Analysis (optional)
- [ ] Time Intelligence (optional)

**Public Link:** _____________________________________________

---

## 📞 If You Get Stuck

**Check these resources:**
- TABLEAU_QUICK_START.md (connection info, formulas)
- TABLEAU_GUIDE.md (detailed instructions)
- Tableau's "Show Me" panel (suggests chart types)
- Tableau Public gallery (inspiration)

**Or ask Echo for help!**

---

**You're building something impressive! Keep going! 🚀**
