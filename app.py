import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from datetime import datetime
import calendar
import io

# Function to fetch data for a given month and year
def fetch_data(month, year):
    url = "http://trifapi.volac.in/api/BudgetExpenses/get"
    
    # Prepare the parameters
    params = {
        "month": month,  # e.g., 'Apr', 'Jan'
        "year": str(year)  # Ensure it's a string
    }
    
    # Make the API call
    response = requests.get(url, params=params, auth=HTTPBasicAuth('API', '7MW6t%"+Vu'))
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()
        if data:
            return pd.DataFrame(data)
        else:
            st.warning(f"No data returned for {month}/{year}")
            return None
    else:
        st.error(f"Failed to fetch data for {month}/{year}. Status Code: {response.status_code}")
        st.text(f"Response Text: {response.text}")
        return None

# Streamlit app interface
st.title("Budget Expense Fetcher")

# Date input for selecting the date range
start_date = st.date_input("Start Date", datetime.today())
end_date = st.date_input("End Date", datetime.today())

# Fetch months and years from the selected date range
months = pd.date_range(start=start_date, end=end_date, freq='MS').strftime('%b')  # Month abbreviation
years = pd.date_range(start=start_date, end=end_date, freq='MS').year

# Display the selected range
st.write(f"Fetching data for the period: {start_date} to {end_date}")

# Button to trigger fetching data
if st.button('Fetch Data'):
    all_data = []
    
    # Loop through months and years in the selected range
    for month, year in zip(months, years):
        st.write(f"Fetching data for {month} {year}...")
        
        # Fetch data for the current month/year
        df = fetch_data(month, year)
        if df is not None:
            all_data.append(df)
    
    # Combine all dataframes into one
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        st.dataframe(final_df)  # Show data in table format
        
        # Excel download functionality
        @st.cache_data  # Cache the result to avoid re-execution
        def to_excel(df):
            # Create an in-memory buffer for the Excel file
            output = io.BytesIO()
            # Write DataFrame to the buffer
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name="Budget Expenses")
            output.seek(0)
            return output

        # Provide a download button
        excel_file = to_excel(final_df)
        st.download_button(
            label="Download Excel",
            data=excel_file,
            file_name="budget_expenses.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No data available for the selected date range.")
