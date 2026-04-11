import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date

# १. क्रेडेंशियल्स (Directly in code to avoid Secret Errors)
GOOGLE_INFO = {
    "type": "service_account",
    "project_id": "organic-storm-492811-i0",
    "private_key_id": "84a2ef9c44445b77bd1c14ad773e99ea59b2785f",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCoDz9z07qGQ9ml\nZEso5J2p+r6AMFVgW2hImfiViAJS4sfGKJwubhLIRH/iYit1YqFsRa4Fw+7cHIdq\nxVmAhu8XCN+0fqFR3oB+CzqzaQLdb28b5EEqvS/0hlVpgMQAOjMFIKczo/622EjI\n7JYin2XdKaNMKo1T+cSHwK1iXOaz1Kk7qegFMIa58D56H5zJRbt+no6d5hPkOjuI\n8RIEw9QeOWIHJZZ2zDocqmzh/DrYPCcAbobMwAmbozG9O08fEGTgiNS/wmyCWdYR\nP7SDvqL8i55AubhpyLlKw7F1ek6HXeYUlP8egq1dxx8y4OT6nDe8RFb73nwuQL3i\nU+ldCXblAgMBAAECggEAAT3lmeE/YFUZg1mXnZR83r/pzvAsfVMHlPvARLiVzc97\nqujraINrM5wf9sgDarFhIHfuVoARYIJ8dKtDI0o784dfAcoqvnxepi/GjgNRYFn9\nr+7SlXKC63Nfp7EqIZdMf7XzTlQgonC8LvHilRxo6Aax/HLXCv8ONvOTRGYL1VnS\nmkh9d6E3Ex6ItafV6lI/+h1tJmX/DFww3NMo6guWfGTXOVGscr5+MqqG6vbp1Jbr\nUuMUkCWfKRhAMwfXv+CHAuxK2ZuXHHhnZQYNDO2kIz+2XswMlinkT3HM6biXhrPT\nkrfZHjz5wcrhEyODto/XoY7L9eDfQjcc5hfOEwRHKQKBgQDVQUZdmjSuG1Obu/Ik\ngyLEOYjTbuCbsO15o1RiPbEPabeO0/DwDnbLGIntQiwWpcK2dp0gTta7/ONEN5Sp\nNcbXTRDXxX5SRGOrbbN6saQXNyq1tpW8JQbQqymx+YXdjXqjetPB7alE+lbBySOd\nnj/OQEjfqDlt3t+gqbOLHucicDQKBgQDJvt3Klfj2cZ5xvgWE4PHGkrc6BVAJp9+a\n5oZ9LtH98P9RVNRLQitvuZml0urQiU5EoWTJ4/nLD4ghtbxwZrInLQOKUBJLHECD\faVMM82Xl3cMe6UrmkdGaeJ/q8uat1r8h9KBvOSDE2iBWhjQbe7+8dnt9WXefDql\llqOpVNOYOQKBgQDHEH+WsHOscmXBYdfOrXquoOZQN5gCvU1v1j7W1a+KK6zk7oJi\nE55gRy+5AaQWH/V6TY6uselQ4edjrl5e9Yv/PjkSsZARSzWeuHBpf5kk8qIzrZRo\nZEfQUXZCZCHJhl+MawNwa2EuumBx1EgitFUvj1IScgR/5HQb5jhrJ8lToQKBgQCK\nnT2I6uyqdujNIA2BBQv4+huM60d2XYRG5XoWhWPH6SLihh6irl8ezpuiheMInCZsx\nDfzNNJBSGGnZwoBYBu/oT8H3lwGToODRxNgIMBOo89xYIISSKgjnSzxPDvZdMYsd\nSfiVnWyEOFATLjOI4XVSL3ia3Pxj1YNXdrjpJBCUcQKBgQDTNLP0WoT89sR+czn3\nr4fUMS6tOwCnUacYDrSwMX2Z8ku7ONcT4R9HaABNMQ05PHvprTc2FfN7Cg9mPaSA\nRLZqgAMVjTrvBytwazk9rvhvosmTmTUPeWY5RsUbehYgUw2dHrrcsjuVoIOCTgv+\nQqyoL22Rz5H6ERq6hXAho/jCEA==\n-----END PRIVATE KEY-----",
    "client_email": "billing-bot@organic-storm-492811-i0.iam.gserviceaccount.com",
    "client_id": "103431109387914808181",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/apps/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/billing-bot%40organic-storm-492811-i0.iam.gserviceaccount.com"
}

# २. पेज सेटअप
st.set_page_config(page_title="Trimurti Smart Tracker", layout="wide")

# ३. गुगल शीट कनेक्शन फंक्शन
def connect_to_sheet():
    try:
        # \n फॉरमॅट फिक्स करणे
        GOOGLE_INFO["private_key"] = GOOGLE_INFO["private_key"].replace("\\n", "\n")
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(GOOGLE_INFO, scopes=scopes)
        client = gspread.authorize(creds)
        # तुझी शीट उघडणे
        sheet = client.open_by_key("1hMy9ETB_wfGGLEE3F6JF1t1AJLOHtR4Gqs_apiJkFss").sheet1
        return sheet
    except Exception as e:
        st.error(f"Error Connecting to Sheet: {e}")
        return None

# ४. मुख्य ॲप लॉजिक
st.title("📞 Trimurti Smart Follow-up")

sheet = connect_to_sheet()

if sheet:
    # डेटा वाचणे
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    if not df.empty:
        # आजचे रिमाइंडर्स
        today = date.today()
        df['Next Date'] = pd.to_datetime(df['Next Date']).dt.date
        
        overdue = df[df['Next Date'] <= today]
        if not overdue.empty:
            st.error(f"🚨 आजचे फॉलो-अप्स: {len(overdue)}")
            st.dataframe(overdue[["Customer Name", "Mobile Number", "Next Date"]], use_container_width=True, hide_index=True)
        
        st.divider()
        
        # ५. डेटा अपडेट (Editor)
        st.subheader("📋 रिपोर्ट अपडेट करा")
        edited_df = st.data_editor(
            df,
            column_config={
                "Status": st.column_config.SelectboxColumn("Status", options=["Pending", "Called", "Interested", "Closed"]),
                "Next Date": st.column_config.DateColumn("पुढची तारीख")
            },
            use_container_width=True, hide_index=True
        )

        if st.button("💾 बदल गुगल शीटमध्ये सेव्ह करा"):
            try:
                # संपूर्ण शीट अपडेट करणे
                sheet.update([edited_df.columns.values.tolist()] + edited_df.astype(str).values.tolist())
                st.success("✅ गुगल शीट अपडेट झाली!")
            except Exception as e:
                st.error(f"सेव्ह करताना एरर: {e}")
    else:
        st.info("शीटमध्ये डेटा नाही.")

# ६. लॉगआउट (पर्यायी)
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
