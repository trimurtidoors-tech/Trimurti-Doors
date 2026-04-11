import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# १. पेज सेटअप
st.set_page_config(page_title="Trimurti Smart Follow-up", layout="wide")

# २. गुगल शीट कनेक्शन (PEM Error सुरक्षित पद्धत)
@st.cache_resource
def get_gsheet_client():
    try:
        info = dict(st.secrets["connections"]["gsheets"])
        # \n ची दुरुस्ती
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"कन्फिगरेशन एरर: {e}")
        return None

SHEET_ID = "1hMy9ETB_wfGGLEE3F6JF1t1AJLOHtR4Gqs_apiJkFss"

# ३. मुख्य ॲप लॉजिक
st.title("📞 Trimurti Marketing Assistant")

client = get_gsheet_client()

if client:
    try:
        sheet = client.open_by_key(SHEET_ID).sheet1
        existing_data = sheet.get_all_records()
        df = pd.DataFrame(existing_data)
        
        # जर शीटमध्ये डेटा नसेल, तर अपलोडचा पर्याय दाखवा
        if df.empty:
            st.warning("⚠️ तुमच्या गुगल शीटमध्ये सध्या कोणताही डेटा नाही.")
            uploaded_file = st.file_uploader("एक्झिक्युटिव्हची '10 April' वाली Excel फाईल अपलोड करा", type=["xlsx"])
            
            if uploaded_file and st.button("शीटमध्ये डेटा पाठवा (One-Time Setup)"):
                df_raw = pd.read_excel(uploaded_file)
                # आपल्याला हवे तसे कॉलम्स तयार करणे
                df_final = pd.DataFrame({
                    "Date": df_raw.get('Date', datetime.now().strftime("%Y-%m-%d")),
                    "Customer Name": df_raw.get('Contact Person Name', 'N/A'),
                    "Category": df_raw.get('Person Status', 'N/A'),
                    "Mobile Number": df_raw.get('Contact No', 'N/A'),
                    "Address": df_raw.get('Address', 'N/A'),
                    "Building Status": df_raw.get('In Progress', 'N/A'),
                    "Status": "Pending",
                    "Next Date": datetime.now().strftime("%Y-%m-%d") # आजची तारीख
                })
                # शीटमध्ये डेटा लिहिणे
                sheet.update([df_final.columns.values.tolist()] + df_final.astype(str).values.tolist())
                st.success("✅ अभिनंदन! डेटा गुगल शीटमध्ये सेव्ह झाला आहे. आता ॲप पुन्हा लोड करा.")
                st.balloons()
        
        else:
            # --- मुख्य फॉलो-अप सिस्टिम ---
            today = date.today()
            df['Next Date'] = pd.to_datetime(df['Next Date']).dt.date
            
            # रिमांडर
            overdue = df[df['Next Date'] <= today]
            if not overdue.empty:
                st.error(f"🚨 **आजचे फॉलो-अप्स ({len(overdue)}):**")
                st.dataframe(overdue[["Customer Name", "Mobile Number", "Next Date"]], use_container_width=True, hide_index=True)

            st.subheader("📋 फॉलो-अप अपडेट करा")
            edited_df = st.data_editor(
                df,
                column_config={
                    "Status": st.column_config.SelectboxColumn("Action", options=["Pending", "Called", "Interested", "Closed"]),
                    "Next Date": st.column_config.DateColumn("पुढची तारीख")
                },
                use_container_width=True, hide_index=True
            )

            if st.button("💾 बदल सेव्ह करा"):
                sheet.update([edited_df.columns.values.tolist()] + edited_df.astype(str).values.tolist())
                st.success("✅ बदल यशस्वीरित्या सेव्ह झाले!")

    except Exception as e:
        st.error(f"डेटा लोड करताना चूक झाली: {e}")
