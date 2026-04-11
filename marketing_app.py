import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# पेज सेटअप
st.set_page_config(page_title="Trimurti Marketing", layout="wide")

st.title("📞 Marketing Follow-up")

# १. गुगल शीट कनेक्शन
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0) # लाइव्ह डेटा वाचणे
except Exception as e:
    st.error(f"शीट कनेक्ट झाली नाही: {e}")
    st.stop()

if not df.empty:
    # २. डेटा फिल्टर करणे (आजचे कॉल्स)
    today = datetime.now().strftime("%Y-%m-%d")
    df['Next Date'] = df['Next Date'].astype(str)
    
    overdue = df[df['Next Date'] <= today]
    if not overdue.empty:
        st.error(f"🚨 आजचे फॉलो-अप्स: {len(overdue)}")
        st.dataframe(overdue[["Customer Name", "Mobile Number", "Next Date"]], use_container_width=True)

    st.divider()

    # ३. स्टेटस आणि डेट अपडेट करण्यासाठी 'Editor'
    st.subheader("📝 अपडेट करा")
    updated_df = st.data_editor(
        df,
        column_config={
            "Status": st.column_config.SelectboxColumn("Status", options=["Pending", "Called", "Interested", "Closed"]),
            "Next Date": st.column_config.DateColumn("पुढचा कॉल")
        },
        use_container_width=True,
        hide_index=True
    )

    # ४. सेव्ह बटण
    if st.button("💾 गुगल शीटमध्ये सेव्ह करा"):
        try:
            conn.update(data=updated_df)
            st.success("✅ डेटा गुगल शीटमध्ये अपडेट झाला!")
            st.balloons()
        except Exception as e:
            st.error(f"सेव्ह करताना एरर: {e}")
else:
    st.info("शीटमध्ये डेटा नाही.")
