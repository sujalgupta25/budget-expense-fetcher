import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from datetime import datetime
import io

# Auth setup
AUTH = HTTPBasicAuth('API', '7MW6t%"+Vu')

# Mapping icons and module order (updated as per your request)
MODULES = {
    "Funding Agency": "🏛️",
    "Project": "📁",
    "Budget Head": "🧾",
    "Sub Budget Head": "📑",
    "Budget": "📊",
    "Budget Expense": "💸"
}

# --- API Fetch Functions ---
def fetch_budget_data(month, year):
    url = "http://trifapi.volac.in/api/BudgetExpenses/get"
    params = {"month": month, "year": str(year)}
    res = requests.get(url, params=params, auth=AUTH)
    df = pd.DataFrame(res.json()) if res.status_code == 200 else pd.DataFrame()
    if not df.empty:
        df["API Month"] = month
        df["API Year"] = year
    return df

def fetch_funding_agency(date):
    url = "http://trifapi.volac.in/api/MasFA/get/"
    params = {"date": date.strftime('%Y-%m-%d')}
    res = requests.get(url, params=params, auth=AUTH)
    df = pd.DataFrame(res.json()) if res.status_code == 200 else pd.DataFrame()
    if not df.empty:
        df["API Date"] = date.strftime('%Y-%m-%d')
    return df

def fetch_project(date):
    url = "http://trifapi.volac.in/api/MasFAPR/GetAllMasFAPR/"
    params = {"date": date.strftime('%Y-%m-%d')}
    res = requests.get(url, params=params, auth=AUTH)
    df = pd.DataFrame(res.json()) if res.status_code == 200 else pd.DataFrame()
    if not df.empty:
        df["API Date"] = date.strftime('%Y-%m-%d')
    return df

def fetch_budget_head(date):
    url = "http://trifapi.volac.in/api/MasBudgetHead/GetAllMasBudgetHead/"
    params = {"date": date.strftime('%Y-%m-%d')}
    res = requests.get(url, params=params, auth=AUTH)
    df = pd.DataFrame(res.json()) if res.status_code == 200 else pd.DataFrame()
    if not df.empty:
        df["API Date"] = date.strftime('%Y-%m-%d')
    return df

def fetch_sub_budget_head(date):
    url = "http://trifapi.volac.in/api/MasSubBudgetHead/GetAllMasSubBudgetHead/"
    params = {"date": date.strftime('%Y-%m-%d')}
    res = requests.get(url, params=params, auth=AUTH)
    df = pd.DataFrame(res.json()) if res.status_code == 200 else pd.DataFrame()
    if not df.empty:
        df["API Date"] = date.strftime('%Y-%m-%d')
    return df

def fetch_budget(date):
    url = "http://trifapi.volac.in/api/MasBU/get/"
    params = {"date": date.strftime('%Y-%m-%d')}
    res = requests.get(url, params=params, auth=AUTH)
    df = pd.DataFrame(res.json()) if res.status_code == 200 else pd.DataFrame()
    if not df.empty:
        df["API Date"] = date.strftime('%Y-%m-%d')
    return df

# Excel Export
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

# --- Streamlit UI ---
st.set_page_config(page_title="Volac Data Fetcher", layout="wide")

# Custom Styling
st.markdown("""
    <style>
        body {
            background-color: #f0f2f6;
        }
        .footer {
            position: relative;
            bottom: 0;
            width: 100%;
            margin-top: 40px;
            text-align: center;
            font-size: 14px;
            color: gray;
        }
        .powered {
            font-weight: bold;
            color: #555;
        }
        .stButton>button {
            background-color: #0066cc;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("📊 Volac Data Fetcher")
st.markdown("Fetch real-time data from Volac APIs")

# Inputs
module = st.selectbox("Select Module", list(MODULES.keys()))
start_date = st.date_input("Start Date", datetime.today())
end_date = st.date_input("End Date", datetime.today())

# Fetch Button
if st.button("📥 Fetch Data"):
    with st.spinner("Fetching data..."):
        df = pd.DataFrame()

        if module == "Funding Agency":
            df = fetch_funding_agency(start_date)

        elif module == "Project":
            df = fetch_project(start_date)

        elif module == "Budget Head":
            df = fetch_budget_head(start_date)

        elif module == "Sub Budget Head":
            df = fetch_sub_budget_head(start_date)

        elif module == "Budget":
            df = fetch_budget(start_date)

        elif module == "Budget Expense":
            months = pd.date_range(start=start_date, end=end_date, freq='MS').strftime('%b')
            years = pd.date_range(start=start_date, end=end_date, freq='MS').year
            all_data = [fetch_budget_data(m, y) for m, y in zip(months, years)]
            df = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

        if not df.empty:
            st.success(f"✅ Data fetched for {module}")
            st.dataframe(df, use_container_width=True)

            # Download button
            st.download_button(
                label="⬇️ Download Excel",
                data=to_excel(df),
                file_name=f"{module.lower().replace(' ', '_')}_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("No data found for the selected inputs.")

# Footer
st.markdown("""
<div class="footer">
    <div class="powered">Powered by: Sujal Gupta</div>
    <div>📧 Contact: sujal.gupta@dhwaniris.com | 📱 7300180072</div>
</div>
""", unsafe_allow_html=True)
