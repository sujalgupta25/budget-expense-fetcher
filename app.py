# Install necessary libraries
!pip install streamlit requests pandas

import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from datetime import datetime, timedelta

# --- API Config ---
API_URL = "http://trifapi.volac.in/api/BudgetExpenses/get"
USERNAME = "API"
PASSWORD = "7MW6t"

# --- UI: Date Inputs ---
st.title("📅 Budget Expense Fetcher")

from_date = st.date_input("Select From Date", datetime.today().replace(day=1))
to_date = st.date_input("Select To Date", datetime.today())

# --- Helper to generate month/year pairs ---
@st.cache_data
def get_month_year_range(start_date, end_date):
    months = []
    current = start_date.replace(day=1)
    while current <= end_date:
        months.append({"month": current.month, "year": current.year})
        next_month = current.replace(day=28) + timedelta(days=4)  # ensures next month
        current = next_month.replace(day=1)
    return months

# --- Fetch data ---
if st.button("Fetch Data"):
    if from_date > to_date:
        st.error("❌ 'From Date' cannot be after 'To Date'")
    else:
        months_years = get_month_year_range(from_date, to_date)
        all_data = []

        with st.spinner("Fetching data..."):
            for item in months_years:
                response = requests.get(
                    API_URL,
                    params={"month": item["month"], "year": item["year"]},
                    auth=HTTPBasicAuth(USERNAME, PASSWORD)
                )
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            all_data.extend(data)
                            st.success(f"Fetched {len(data)} records for {item['month']}/{item['year']}")
                        else:
                            st.warning(f"No data returned for {item['month']}/{item['year']}")
                    except ValueError:
                        st.error(f"Failed to parse data for {item['month']}/{item['year']}")
                else:
                    st.error(f"API call failed for {item['month']}/{item['year']}")

        # --- Show data ---
        if all_data:
            df = pd.DataFrame(all_data)
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", csv, "budget_expenses.csv", "text/csv")
        else:
            st.info("No data retrieved in the selected range.")
