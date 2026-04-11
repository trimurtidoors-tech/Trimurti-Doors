import streamlit as st
from fpdf import FPDF
from datetime import date
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import os

# १. पेज सेटिंग्ज
st.set_page_config(page_title="Trimurti Doors World", layout="wide")

# २. गुगल शीट कनेक्शन
conn = st.connection("gsheets", type=GSheetsConnection)

# ३. दरांचे व्यवस्थापन
RATES_FILE = "rates_data.json"
def load_rates():
    default_rates = {"FT": 720, "Deco": 685, "PD": 585, "Delux": 385, "Diamond": 315, "Classic": 285, "Silver": 240, "FRP": 185, "Ls": 240, "T": 160, "Eg": 630}
    if os.path.exists(RATES_FILE):
        with open(RATES_FILE, "r") as f: return json.load(f)
    return default_rates

def save_rates(rates):
    with open(RATES_FILE, "w") as f: json.dump(rates, f)

# ४. युजर लॉगिन
USERS = {"Dhananjay": "Trimurti@2026", "Admin": "Admin@123", "Abhijit_Choudhari": "123"}

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'all_entries' not in st.session_state: st.session_state.all_entries = []
if 'rates' not in st.session_state: st.session_state.rates = load_rates()

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>🔐 Login</h2>", unsafe_allow_html=True)
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u in USERS and p == USERS[u]:
            st.session_state.logged_in = True
            st.session_state.current_user = u
            st.rerun()
        else: st.error("Invalid Login!")
else:
    st.markdown(f"<div style='background-color:#004aad;padding:10px;color:white;text-align:center;border-radius:10px;'><h1>TRIMURTI DOORS WORLD</h1></div>", unsafe_allow_html=True)

    # एडमिन सेटिंग्स
    if st.session_state.current_user == "Dhananjay":
        with st.expander("⚙️ Admin Settings"):
            new_r = {}
            cols = st.columns(4)
            for idx, (k, v) in enumerate(st.session_state.rates.items()):
                new_r[k] = cols[idx % 4].number_input(f"{k} Rate", value=float(v))
            if st.button("Save New Rates"):
                st.session_state.rates = new_r
                save_rates(new_r); st.success("Rates Updated!")

    # इंच कन्वर्शन
    INCH_CONV = {0.1: 0.125, 0.2: 0.250, 0.3: 0.375, 0.4: 0.500, 0.5: 0.625, 0.6: 0.750, 0.7: 0.875, 0.8: 1.0, 0.9: 1.125}
    def get_val(v):
        m = int(v); f = round(v - m, 1)
        return m + INCH_CONV.get(f, f)

    # ७. कस्टमर माहिती
    st.markdown("### 👤 Customer Details")
    c1, c2, c3 = st.columns([1, 1, 2])
    cust_name = c1.text_input("Customer Name")
    mobile = c2.text_input("Mobile No.")
    address = c3.text_input("Address")

    # ८. डोअर एन्ट्री फॉर्म
    with st.form("door_form", clear_on_submit=True):
        st.markdown("##### ➕ Add Door Item")
        r = st.columns(7)
        ser = r[0].selectbox("Series", list(st.session_state.rates.keys()))
        qty = r[1].number_input("Qty", min_value=1, step=1)
        des = r[2].text_input("Design")
        col = r[3].text_input("Color")
        h_in = r[4].number_input("Height", format="%.1f")
        w1_in = r[5].number_input("W-Top", format="%.1f")
        w2_in = r[6].number_input("W-Bottom", format="%.1f")
        if st.form_submit_button("ADD TO LIST"):
            fh, fw1, fw2 = get_val(h_in), get_val(w1_in), get_val(w2_in)
            sqft = round(max(14.0, (fh * max(fw1, fw2)) / 144), 2)
            st.session_state.all_entries.append({
                "Series": ser, "Design": des, "Color": col, "H": fh, "W1": fw1, "W2": fw2,
                "Qty": qty, "SqFt": sqft, "Rate": st.session_state.rates[ser], "Total": round(sqft * qty * st.session_state.rates[ser], 2)
            })
            st.rerun()

    # ९. बिलिंग कॅल्क्युलेशन
    if st.session_state.all_entries:
        st.markdown("### 📋 Current Items")
        st.table(st.session_state.all_entries)
        
        sub_val = sum(i['Total'] for i in st.session_state.all_entries)
        f_cols = st.columns(4)
        gst_p = f_cols[0].number_input("GST %", 0)
        trans = f_cols[1].number_input("Transport", 0)
        adv = f_cols[2].number_input("Advance", 0)
        disc = f_cols[3].number_input("Discount", 0)
        
        gst_amt = round((sub_val * gst_p) / 100, 2)
        grand = sub_val + gst_amt + trans - disc - adv
        st.subheader(f"💰 Grand Total: ₹ {grand:,.2f}")

        # १०. सेव्ह आणि पीडीएफ
        if st.button("🚀 FINALIZE & SAVE"):
            try:
                # गुगल शीट सिंक - बरोबर १९ रकाने
                try: df_existing = conn.read(ttl=0)
                except: df_existing = pd.DataFrame()

                new_rows = []
                for e in st.session_state.all_entries:
                    new_rows.append({
                        "Date": str(date.today()), "User": st.session_state.current_user,
                        "Customer": cust_name, "Mobile": f"'{mobile}", "Address": address,
                        "Qty": e['Qty'], "Series": e['Series'], "Design": e['Design'], "Color": e['Color'],
                        "H": e['H'], "W1": e['W1'], "W2": e['W2'], "SqFt": e['SqFt'], "Rate": e['Rate'], 
                        "GST_Amt": gst_amt, "Transport": trans, "Advance": adv, "Discount": disc, 
                        "Final_Bill": grand # हा १९ वा रकाना 'S' वर येईल
                    })
                
                df_updated = pd.concat([df_existing, pd.DataFrame(new_rows)], ignore_index=True)
                conn.update(data=df_updated)
                st.success("Data successfully saved up to Column S!")
            except Exception as e: st.error(f"Sync Error: {e}")

            # पीडीएफ तयार करणे
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", 'B', 16)
            pdf.cell(190, 10, "TRIMURTI DOORS WORLD", 0, 1, 'C')
            pdf.set_font("Arial", '', 10)
            pdf.cell(190, 7, f"Customer: {cust_name} | Mob: {mobile}", 0, 1)
            pdf.cell(190, 7, f"Address: {address} | Date: {date.today()}", 0, 1); pdf.ln(5)
            
            pdf.set_font("Arial", 'B', 8); pdf.set_fill_color(230, 230, 230)
            h_list = ["Sr", "Series", "Qty", "H", "W1", "W2", "SqFt", "Rate", "Total"]
            w_list = [10, 25, 15, 20, 20, 20, 20, 20, 40]
            for idx, h in enumerate(h_list): pdf.cell(w_list[idx], 10, h, 1, 0, 'C', True)
            pdf.ln(); pdf.set_font("Arial", '', 8)
            for idx, item in enumerate(st.session_state.all_entries):
                pdf.cell(w_list[0], 8, str(idx+1), 1)
                pdf.cell(w_list[1], 8, item['Series'], 1); pdf.cell(w_list[2], 8, str(item['Qty']), 1)
                pdf.cell(w_list[3], 8, str(item['H']), 1); pdf.cell(w_list[4], 8, str(item['W1']), 1)
                pdf.cell(w_list[5], 8, str(item['W2']), 1); pdf.cell(w_list[6], 8, str(item['SqFt']), 1)
                pdf.cell(w_list[7], 8, str(item['Rate']), 1); pdf.cell(w_list[8], 8, str(item['Total']), 1, 1, 'R')
            
            pdf.ln(5); pdf.set_font("Arial", 'B', 10)
            pdf.cell(150, 7, f"Subtotal: {sub_val:,.2f} | GST: {gst_amt:,.2f} | Trans: {trans:,.2f}", 0, 1, 'R')
            pdf.cell(150, 7, f"Discount: -{disc:,.2f} | Advance: -{adv:,.2f}", 0, 1, 'R')
            pdf.set_font("Arial", 'B', 12); pdf.cell(190, 10, f"GRAND TOTAL: Rs. {grand:,.2f}", 0, 1, 'R')
            
            st.download_button("📥 DOWNLOAD PDF", data=pdf.output(dest='S').encode('latin-1'), file_name=f"Trimurti_{cust_name}.pdf")

    if st.button("🚪 Logout"):
        st.session_state.all_entries = []; st.session_state.logged_in = False; st.rerun()
