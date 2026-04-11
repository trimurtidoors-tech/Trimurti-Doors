import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# १. पेज सेटअप
st.set_page_config(page_title="Trimurti Smart Follow-up", layout="wide")

# २. एजंट लॉगिन माहिती
AGENTS = {"Dhananjay": "789", "Jitesh": "101"}
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Agent Login")
    user = st.text_input("ID")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user in AGENTS and pw == AGENTS[user]:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("चुकीचा पासवर्ड!")
else:
    st.title("📞 Trimurti Marketing & Follow-up")
    
    # ३. फाईल अपलोडर (Excel - xlsx सपोर्ट)
    st.sidebar.header("Data Upload")
    uploaded_file = st.sidebar.file_uploader("एक्झिक्युटिव्हची Excel फाईल निवडा", type=["xlsx", "xls"])

    if uploaded_file:
        try:
            # Excel वाचणे
            df_raw = pd.read_excel(uploaded_file)
            
            # तुझ्या म्हणण्यानुसार डेटाची मांडणी (Sequence):
            # Name -> Category -> Mobile -> Building Status -> Address -> Executive Remark
            df_display = pd.DataFrame({
                "Customer Name": df_raw.get('Contact Person Name', 'N/A'),
                "Category": df_raw.get('Person Status', 'N/A'),
                "Mobile": df_raw.get('Contact No', 'N/A'),
                "Building Status": df_raw.get('In Progress', 'N/A'),
                "Address": df_raw.get('Address', 'N/A'),
                "Executive Remark": df_raw.get('Remark', 'N/A'),
                "Follow-up Status": "Pending", 
                "Next Call Date": (datetime.now().date()) # आजची तारीख डिफॉल्ट
            })

            # ४. टॅब सिस्टिम (कामाचे नियोजन)
            tab1, tab2 = st.tabs(["🎯 आजचे कॉल्स (Today's Tasks)", "📋 सर्व डेटा (Full Report)"])

            with tab1:
                today = datetime.now().date()
                # ज्यांची 'Next Call Date' आजची आहे असे लोक
                calls_today = df_display[df_display['Next Call Date'] <= today]
                
                if not calls_today.empty:
                    st.warning(f"🚨 आज तुम्हाला {len(calls_today)} क्लायंट्सना फॉलो-अप द्यायचा आहे!")
                    st.data_editor(
                        calls_today[["Customer Name", "Category", "Mobile", "Follow-up Status", "Next Call Date"]], 
                        use_container_width=True, 
                        hide_index=True
                    )
                else:
                    st.success("✅ आजसाठी कोणतेही प्रलंबित कॉल्स नाहीत!")

            with tab2:
                st.subheader("संपूर्ण व्हिजिट रिपोर्ट आणि अपडेट्स")
                # इथे तू सगळा डेटा एडिट करू शकतोस
                updated_df = st.data_editor(
                    df_display,
                    column_config={
                        "Follow-up Status": st.column_config.SelectboxColumn(
                            "My Action",
                            options=["Pending", "Called - Interested", "Call in 15 Days", "Call in 1 Month", "Meeting Set", "Closed"],
                            required=True
                        ),
                        "Next Call Date": st.column_config.DateColumn("Next Follow-up")
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                # ५. सेव्ह करण्याचा पर्याय (CSV Download)
                st.divider()
                if st.button("💾 बदल सेव्ह करा"):
                    csv = updated_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 अपडेटेड रिपोर्ट डाउनलोड करा",
                        data=csv,
                        file_name=f"Marketing_Update_{datetime.now().strftime('%d_%b')}.csv",
                        mime="text/csv",
                    )
                    st.success("बदल तयार आहेत, कृपया वरील बटण दाबून फाईल सेव्ह करा.")

        except Exception as e:
            st.error(f"Error: {e}")
            st.info("टीप: तुम्ही requirements.txt मध्ये 'openpyxl' टाकले असल्याची खात्री करा.")
    else:
        st.info("👈 कृपया बाजूच्या मेनूमधून एक्झिक्युटिव्हची Excel फाईल अपलोड करा.")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
