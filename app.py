import streamlit as st
import sqlite3
import random

# Global application frame config
st.set_page_config(page_title="Y999 Matrix System", page_icon="🎰", layout="wide")

# --- MALAYSIAN CORE BANKS CONFIG ---
MALAYSIAN_BANKS = [
    "Maybank (Malayan Banking Berhad)",
    "CIMB Bank Berhad",
    "Public Bank Berhad",
    "RHB Bank Berhad",
    "Hong Leong Bank Berhad",
    "AmBank (M) Berhad"
]

# --- LIGHTWEIGHT LOCAL STORAGE DB ---
def init_db():
    conn = sqlite3.connect("matrix_vault.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            balance REAL,
            liquidation REAL,
            active_level TEXT,
            ref_code TEXT
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
    except Exception:
        conn.close()
        return None if one else []

# System Route Handlers
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'auth_view' not in st.session_state: st.session_state.auth_view = "login"
if 'selected_panel' not in st.session_state: st.session_state.selected_panel = "Dashboard Overview"

# --- INJECTING PREMIUM FONTS & THEME ENGINE ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap" rel="stylesheet">
    
    <style>
    /* Hide Default Streamlit Overlays */
    footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stSidebar"] { 
        display: none !important; visibility: hidden !important;
    }
    
    /* Cyberpunk Space Background Gradient */
    html, body, .stApp { 
        background: linear-gradient(135deg, #0a0a1a 0%, #0d0d2b 40%, #1a0a2e 70%, #0a1a2e 100%) !important;
        color: #e0e0ff !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    
    /* Elegant Translucent Blurry Containers */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(15, 10, 40, 0.85) !important;
        border: 1px solid rgba(255, 105, 180, 0.3) !important;
        border-radius: 20px !important;
        padding: 30px !important;
        box-shadow: 0 0 40px rgba(255,105,180,0.15), 0 0 80px rgba(135,206,235,0.08), inset 0 1px 0 rgba(255,255,255,0.05) !important;
        backdrop-filter: blur(20px) !important;
    }
    
    /* Typography Global Reset to Cyberpunk Specs */
    label, p, span, li {
        color: rgba(135,206,235,0.8) !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        letter-spacing: 1px !important;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900 !important;
        letter-spacing: 2px !important;
    }
    
    /* Animated Glowing Header System */
    .shimmer-logo {
        font-family: 'Orbitron', sans-serif;
        font-size: 38px;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #ff69b4, #87ceeb, #ff1493, #00bfff);
        background-size: 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 3s linear infinite;
        letter-spacing: 3px;
        margin-bottom: 5px;
    }
    @keyframes shimmer {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    
    /* FIX: Input Fields Text Color Visibility Solution */
    div[data-testid="stTextInput"] input, 
    div[data-testid="stNumberInput"] input, 
    div[data-testid="stSelectbox"] div {
        background: #ffffff !important; /* Input box background white rahega */
        color: #111111 !important;    /* Text bilkul dark black ho jayega taake saaf dikhe */
        -webkit-text-fill-color: #111111 !important; /* Mobile browsers ke liye fix */
        border: 1px solid rgba(255,105,180,0.4) !important;
        border-radius: 10px !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700 !important;
    }
    
    /* Placeholder Text Alignment */
    div[data-testid="stTextInput"] input::placeholder {
        color: #888888 !important;
        -webkit-text-fill-color: #888888 !important;
    }
    
    div[data-testid="stTextInput"] input:focus {
        border-color: rgba(255,105,180,0.8) !important;
        box-shadow: 0 0 12px rgba(255,105,180,0.3) !important;
    }

    /* AUTH AND ACTION MAIN BUTTONS */
    div.stButton > button {
        background: linear-gradient(135deg, #ff1493, #ff69b4) !important;
        color: #ffffff !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 20px rgba(255,20,147,0.4) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        filter: brightness(1.15) !important;
    }

    /* SPECIFIC INNER NAVIGATION MODULE BUTTONS */
    .nav-container div.stButton > button {
        background: rgba(15, 10, 40, 0.6) !important;
        color: #e0e0ff !important;
        border: 1px solid rgba(135,206,235,0.3) !important;
        box-shadow: none !important;
        text-align: left !important;
    }
    .nav-container div.stButton > button:hover {
        border-color: rgba(135,206,235,0.8) !important;
        box-shadow: 0 0 15px rgba(135,206,235,0.2) !important;
        color: #87ceeb !important;
    }
    
    /* Premium Twin Balance Display Grid */
    .balance-card-container {
        display: flex;
        gap: 15px;
        margin-bottom: 25px;
    }
    .balance-box {
        flex: 1;
        background: rgba(15, 10, 40, 0.7);
        border: 1px solid rgba(255, 105, 180, 0.25);
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 0 20px rgba(255,105,180,0.05);
    }
    .balance-title {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: rgba(135,206,235,0.6);
        margin-bottom: 6px;
    }
    .balance-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 20px;
        font-weight: 900;
        color: #ff69b4 !important;
    }
    .balance-value-sky {
        font-family: 'Orbitron', sans-serif;
        font-size: 20px;
        font-weight: 900;
        color: #87ceeb !important;
    }

    /* Dashed Promo Strip */
    .promo-banner {
        background: rgba(255,105,180,0.05);
        border: 1px dashed rgba(255,105,180,0.3);
        padding: 12px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
        font-size: 14px;
    }
    .text-pink-neon { color: #ff69b4 !important; font-weight: bold; }
    
    /* Social Media Shortcut Rows */
    .social-row {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 20px;
    }
    .social-btn {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# --- AUTH LAYER ---
if not st.session_state.logged_in:
    st.markdown("<div class='shimmer-logo'> 💵 ONLINE EARNINGS</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color: rgba(135,206,235,0.7); letter-spacing:2px; text-transform:uppercase; font-size:11px; margin-bottom:20px;'>Secured Authorization Node</p>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div class="promo-banner">
             Invite a friend and get a bonus of <span class="text-pink-neon">RM 50</span><br>
             Download the app and get a bonus of <span class="text-pink-neon">RM 100 - 999</span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.auth_view == "login":
            st.markdown("<h3 style='font-size:16px; color:#ff69b4; border-bottom:1px solid rgba(255,105,180,0.2); padding-bottom:8px; margin-bottom:15px;'>LOGIN TO ACCOUNT</h3>", unsafe_allow_html=True)
            
            user_input = st.text_input("Registered Phone number / Email Address", placeholder="Please enter Phone/Email")
            pass_input = st.text_input("System Security Password", type="password", placeholder="Enter password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Verify"):
                if user_input.strip() and pass_input.strip():
                    record = query_db("SELECT password FROM users WHERE username=?", (user_input.strip(),), one=True)
                    if not record:
                        m_code = "Y" + str(random.randint(100, 999))
                        query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                                 (user_input.strip(), pass_input.strip(), 3672, 22930.00, "SVIP LEVEL 9", m_code), commit=True)
                        record = [pass_input.strip()]
                    
                    if record[0] == pass_input.strip():
                        st.session_state.logged_in = True
                        st.session_state.current_user = user_input.strip()
                        st.session_state.selected_panel = "Dashboard Overview"
                        st.rerun()
            
            st.markdown("<p style='text-align:center; margin-top:15px; font-size:13px;'>Don't have an asset profile account?</p>", unsafe_allow_html=True)
            if st.button("Create Profile Account"):
                st.session_state.auth_view = "signup"
                st.rerun()
                
        else:
            st.markdown("<h3 style='font-size:16px; color:#ff69b4; border-bottom:1px solid rgba(255,105,180,0.2); padding-bottom:8px; margin-bottom:15px;'>REGISTER SECURE PROFILE</h3>", unsafe_allow_html=True)
            
            reg_user = st.text_input("Account Phone number / Email", placeholder="Please enter Phone/Email")
            reg_pass = st.text_input("Setup Password security", type="password", placeholder="Enter password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Confirm Registration"):
                if reg_user.strip() and reg_pass.strip():
                    m_code = "Y" + str(random.randint(100, 999))
                    query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                             (reg_user.strip(), reg_pass.strip(), 77889900.00, 54522930.00, "SVIP LEVEL 9", m_code), commit=True)
                    st.session_state.logged_in = True
                    st.session_state.current_user = reg_user.strip()
                    st.session_state.selected_panel = "Dashboard Overview"
                    st.rerun()
            
            if st.button("Back to Login Hub"):
                st.session_state.auth_view = "login"
                st.rerun()

        st.markdown("<div style='text-align:center; color:rgba(135,206,235,0.4); margin-top:25px; font-size:12px; letter-spacing:1px;'>— BINDING REGISTRATION SHORTCUTS —</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="social-row">
            <div class="social-btn"><img src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg" width="20"></div>
            <div class="social-btn"><img src="https://upload.wikimedia.org/wikipedia/commons/b/b8/2021_Facebook_icon.svg" width="20"></div>
            <div class="social-btn"><img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" width="20"></div>
        </div>
        """, unsafe_allow_html=True)

# --- PANEL LAYER ---
else:
    user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code FROM users WHERE username=?", (st.session_state.current_user,), one=True)
    wallet_bal, liquid_bal, level_tag, reference_hash = user_metrics if user_metrics else (77889900.00, 54522930.00, "SVIP LEVEL 9", "Y999")
    
    st.markdown(f"""
    <div class="balance-card-container">
        <div class="balance-box">
            <div class="balance-title">My Earnings Balance</div>
            <div class="balance-value">RM {wallet_bal:,.2f}</div>
        </div>
        <div class="balance-box">
            <div class="balance-title"> Ready For Cashout</div>
            <div class="balance-value-sky">RM {liquid_bal:,.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h4 style='font-family:\"Orbitron\", sans-serif; font-size:12px; color:rgba(135,206,235,0.6) !important; margin-bottom:12px;'>🧭 SYSTEM NAVIGATION INDEX</h4>", unsafe_allow_html=True)

    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    
    if st.button("🎰 Fund Deposit / Overview Hub"):
        st.session_state.selected_panel = "Dashboard Overview"
        st.rerun()
        
    if st.button("🎥 Claim Revenue / Video Task Node"):
        st.session_state.selected_panel = "Stream Video Tasks"
        st.rerun()
        
    if st.button(" Add Wallet Balance Node"):
        st.session_state.selected_panel = "Add Wallet Funds"
        st.rerun()
        
    if st.button(" Bank Cashout Liquidation Protocol"):
        st.session_state.selected_panel = "Bank Cashout"
        st.rerun()
        
    if st.button("Ledger Session Logs"):
        st.session_state.selected_panel = "Ledger Logs"
        st.rerun()
        
    if st.button(" Disconnect Secure Session"):
        st.session_state.logged_in = False
        st.session_state.auth_view = "login"
        st.rerun()

    st.markdown('</div><br>', unsafe_allow_html=True)
    
    st.markdown("<div style='background: rgba(15,10,40,0.85); padding:20px; border-radius:14px; border:1px solid rgba(255,105,180,0.2);'>", unsafe_allow_html=True)
    
    if st.session_state.selected_panel == "Dashboard Overview":
        st.markdown(f"<h3 style='font-size:18px; color:#ff69b4 !important;'>Active Workspace Tracker</h3>", unsafe_allow_html=True)
        st.write(f"Account Profile Level Rank: {level_tag}")
        st.write(f"Unique Master Invitation Link Code: {reference_hash}")
        st.info("System Engine operational. All tracking nodes are online.")
        
    elif st.session_state.selected_panel == "Stream Video Tasks":
        st.markdown("<h3 style='font-size:18px; color:#ff69b4 !important;'>Video Streams Premium Rewards</h3>", unsafe_allow_html=True)
        st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        if st.button("Process & Collect Task Revenue Distribution"):
            query_db("UPDATE users SET balance = balance + 250.00 WHERE username=?", (st.session_state.current_user,), commit=True)
            st.success("Reward allocated successfully! +RM 250.00")
            st.rerun()
            
    elif st.session_state.selected_panel == "Add Wallet Funds":
        st.markdown("<h3 style='font-size:18px; color:#ff69b4 !important;'>Submit Local Malaysian Bank Proof Slip</h3>", unsafe_allow_html=True)
        st.selectbox("Select Destination Network Bank Node:", MALAYSIAN_BANKS)
        st.text_input("Remitter / Account Holder Full Name:")
        st.text_input("Unique System Transaction Reference ID (Trx ID):")
        if st.button("File Proof Settlement Entry"):
            st.success("Verification slip submitted to admin vault successfully.")
            
    elif st.session_state.selected_panel == "Bank Cashout":
        st.markdown("<h3 style='font-size:18px; color:#ff69b4 !important;'>Configure Outflow Liquidation Settlement</h3>", unsafe_allow_html=True)
        st.selectbox("Select Bank Infrastructure Module:", MALAYSIAN_BANKS)
        st.text_input("Target Clearing Bank Account Number:")
        st.number_input("Liquidation Inflow Allocation Volume (RM):", min_value=10.0)
        if st.button("Initialize Instant Cashout Framework"):
            st.error("Operation failed. Core balance limit constraints reached.")
            
    elif st.session_state.selected_panel == "Ledger Logs":
        st.markdown("<h3 style='font-size:18px; color:#ff69b4 !important;'>Account Financial Ledger Sheets</h3>", unsafe_allow_html=True)
        st.warning("No tracking logs recorded on this session index.")
        
    st.markdown("</div>", unsafe_allow_html=True)
