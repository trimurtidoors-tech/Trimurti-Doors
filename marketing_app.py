import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# १. पेज सेटअप
st.set_page_config(page_title="Trimurti Smart Follow-up", layout="wide")

# २. गुगल शीट कनेक्शन (Safe Method)
@st.cache_resource
def get_gsheet_client():
    try:
        # Secrets मधून क्रेडेंशियल्स मिळवणे
        info = dict(st.secrets["connections"]["gsheets"])
        # PEM Error टाळण्यासाठी \n दुरुस्त करणे
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"कन्फिगरेशन एरर: {e}")
        return None

# ३. डेटा वाचणे आणि सेव्ह करणे
SHEET_ID = "1hMy9ETB_wfGGLEE3F6JF1t1AJLOHtR4Gqs_apiJkFss"

def load_data():
    client = get_gsheet_client()
    if client:
        sheet = client.open_by_key(SHEET_ID).sheet1
        data = sheet.get_all_records()
        return pd.DataFrame(data), sheet
    return pd.DataFrame(), None

# ४. मुख्य इंटरफेस
st.title("📞 Trimurti Marketing Assistant")

df, sheet = load_data()

if not df.empty:
    # आजचे रिमाइंडर्स (Notification)
    today = date.today()
    # 'Next Date' कॉलममधील तारखा डिकोड करणे
    df['Next Date'] = pd.to_datetime(df['Next Date']).dt.date
    
    overdue = df[df['Next Date'] <= today]
    
    if not overdue.empty:
        st.error(f"🚨 **आजचे फॉलो-अप्स ({len(overdue)}):**")
        st.dataframe(overdue[["Customer Name", "Mobile Number", "Next Date"]], use_container_width=True, hide_index=True)
    else:
        st.success("✅ आज कोणतेही प्रलंबित कॉल्स नाहीत.")

    st.divider()

    # ५. डेटा अपडेट विभाग
    st.subheader("📋 फॉलो-अप अपडेट करा")
    
    # डेटा एडिटर - इथे तू स्टेटस आणि तारीख बदलू शकतोस
    edited_df = st.data_editor(
        df,
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Action",
                options=["Pending", "Called", "Interested", "Visit Done", "Closed"],
                required=True
            ),
            "Next Date": st.column_config.DateColumn("पुढची तारीख")
        },
        use_container_width=True,
        hide_index=True
    )

    if st.button("💾 बदल गुगल शीटमध्ये सेव्ह करा"):
        try:
            # पूर्ण शीट अपडेट करणे
            sheet.update([edited_df.columns.values.tolist()] + edited_df.astype(str).values.tolist())
            st.success("✅ गुगल शीट यशस्वीरित्या अपडेट झाली!")
            st.balloons()
        except Exception as e:
            st.error(f"सेव्ह करताना अडचण आली: {e}")

else:
    st.info("शीटमध्ये डेटा नाही किंवा लोड होत नाहीये.")

# ६. नवीन फाईल अपलोड करण्याचा पर्याय (फक्त सुरुवातीला)
with st.expander("📂 नवीन एक्झिक्युटिव्ह फाईल इथून जोडा"):
    uploaded_file = st.file_uploader("Excel फाईल निवडा", type=["xlsx"])
    if uploaded_file and st.button("शीटमध्ये ओव्हरराईट करा"):
        new_df = pd.read_excel(uploaded_file)
        # आवश्यक कॉलम्स मॅप करा (Name, Mobile, Category, इ.)
        # ... (इथे आपण तुझा जुना मॅपिंग कोड वापरू शकतो)
        st.warning("हे केल्यास जुना डेटा पुसला जाईल. खात्री आहे?")
