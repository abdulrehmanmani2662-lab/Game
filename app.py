import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="GLOBAL MATRIX", page_icon="👑", layout="wide")

# --- DATABASE ENGINE ---
def init_db():
    conn = sqlite3.connect("matrix_vault.db")
    cursor = conn.cursor()
    # Check if table exists, if not create it
    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL)")
    # Default admin
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'admin123', 0.0)")
    # Deposits table
    cursor.execute("CREATE TABLE IF NOT EXISTS deposits (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, amount REAL, status TEXT, date TEXT)")
    conn.commit()
    conn.close()

init_db()

def query_db(query, args=(), one=False):
    conn = sqlite3.connect("matrix_vault.db")
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

# --- CYBERPUNK STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;700&display=swap');
    .stApp { background: radial-gradient(circle at center, #131021 0%, #06040f 100%) !important; font-family: 'Rajdhani', sans-serif !important; color: #fff !important; }
    .card { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border-left: 5px solid #00ffcc; margin-bottom: 15px; }
    h1, h2, h3, h4 { color: #00ffcc !important; text-shadow: 0 0 10px #00ffcc; }
    div.stButton > button { width: 100%; border: 1px solid #ff007f !important; background: rgba(255, 0, 127, 0.1) !important; color: #ff007f !important; font-weight: bold; border-radius: 8px; transition: 0.3s; }
    div.stButton > button:hover { background: #ff007f !important; color: #fff !important; box-shadow: 0 0 15px #ff007f; }
    .stTextInput > div > div > input { background-color: #1a1a2e !important; color: white !important; border: 1px solid #ff007f !important; }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None

# --- APP FLOW ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>👑 GLOBAL MATRIX LOGIN</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["LOGIN", "REGISTER"])
    
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("AUTHORIZE ACCESS"):
            # ID check logic
            user_rec = query_db("SELECT * FROM users WHERE username=?", (u.strip(),), one=True)
            if user_rec and user_rec[1] == p.strip():
                st.session_state.logged_in = True
                st.session_state.user = u.strip()
                st.rerun()
            else:
                st.error("Access Denied: Invalid Credentials!")

    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("CREATE ACCOUNT"):
            try:
                query_db("INSERT INTO users VALUES (?, ?, 0.0)", (nu.strip(), np.strip()))
                st.success("Account initialized! Go to Login tab.")
            except:
                st.error("Error: Username already exists.")

else:
    st.markdown(f"### Welcome Operator: {st.session_state.user}")
    
    # Dashboard Card
    u_bal = query_db("SELECT balance FROM users WHERE username=?", (st.session_state.user,), one=True)
    st.markdown(f'<div class="card"><h4>Wallet Balance: RM {u_bal[0]:.2f}</h4></div>', unsafe_allow_html=True)
    
    # Deposit Section
    with st.expander("💰 DEPOSIT FUNDS"):
        amt = st.number_input("Enter Amount", min_value=1.0)
        if st.button("CONFIRM TRANSACTION"):
            query_db("INSERT INTO deposits (username, amount, status, date) VALUES (?, ?, ?, ?)", 
                     (st.session_state.user, amt, 'Pending', datetime.now().strftime("%Y-%m-%d")))
            st.toast("Deposit initiated. Waiting for admin approval.")

    # History Table
    st.markdown("#### 📜 Recent Transactions")
    hist = query_db("SELECT amount, status, date FROM deposits WHERE username=?", (st.session_state.user,))
    if hist:
        df = pd.DataFrame(hist, columns=["Amount", "Status", "Date"])
        st.table(df)

    if st.button("LOG OUT"):
        st.session_state.logged_in = False
        st.rerun()
