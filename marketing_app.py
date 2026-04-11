import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. Page Setup
st.set_page_config(page_title="Trimurti Marketing Follow-up", layout="wide")

# 2. Styling (Visual Alert sathi)
st.markdown("""
    <style>
    .followup-alert { color: white; background-color: #FF4B4B; padding: 10px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar - File Upload
st.sidebar.header("Data Management")
uploaded_file = st.sidebar.file_uploader("Executive chi CSV file upload kara", type="csv")

# Session state madhye data save karne
if 'marketing_data' not in st.session_state:
    st.session_state.marketing_data = pd.DataFrame(columns=[
        "Date", "Customer Name", "Category", "Mobile Number", "Address", "Building Status", "Follow-up Status", "Next Date"
    ])

# File upload jhali ki data process karne
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    # File madhale columns map karne
    temp_df = pd.DataFrame({
        "Date": df.get('Date', datetime.now().strftime("%Y-%m-%d")),
        "Customer Name": df.get('Contact Person Name', 'N/A'),
        "Category": df.get('Person Status', 'N/A'),
        "Mobile Number": df.get('Contact No', 'N/A'),
        "Address": df.get('Address', 'N/A'),
        "Building Status": df.get('In Progress', 'N/A'),
        "Follow-up Status": "Pending",
        "Next Date": datetime.now().date()
    })
    st.session_state.marketing_data = temp_df
    st.success("Data Upload Jhala!")

# 4. Main App Interface
st.title("📞 Trimurti Follow-up Tracker")

# Notification Section (Alert)
today = datetime.now().date()
upcoming = st.session_state.marketing_data[st.session_state.marketing_data['Next Date'] <= today]

if not upcoming.empty:
    st.markdown(f'<div class="followup-alert">🔔 Lakshya dya! Aaj tuche {len(upcoming)} Follow-ups baki ahet!</div>', unsafe_allow_html=True)
    st.dataframe(upcoming[["Customer Name", "Mobile Number", "Next Date"]])

st.divider()

# 5. Data Editor (Status Update sathi)
st.subheader("📋 Sarv Data (Update Status Here)")
edited_df = st.data_editor(
    st.session_state.marketing_data,
    column_config={
        "Follow-up Status": st.column_config.SelectboxColumn(
            "Call Status",
            options=["Pending", "Called - Busy", "Follow-up Set", "Interested", "Closed"],
            required=True,
        ),
        "Next Date": st.column_config.DateColumn("Next Follow-up Date")
    },
    hide_index=True,
    use_container_width=True
)

if st.button("💾 Changes Save Kara"):
    st.session_state.marketing_data = edited_df
    st.success("Status ani Dates Update jhalya!")

# 6. Filters
st.sidebar.divider()
st.sidebar.subheader("Filters")
selected_cat = st.sidebar.multiselect("Category Nivada", options=st.session_state.marketing_data['Category'].unique())
if selected_cat:
    st.session_state.marketing_data = st.session_state.marketing_data[st.session_state.marketing_data['Category'].isin(selected_cat)]
