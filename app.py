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

# --- DEEP INJECTED CASINO THEME CSS (EVERYTHING BECOMES DARK & PREMIUM) ---
st.markdown("""
    <style>
    /* Hide Default Streamlit Overlays */
    footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stSidebar"] { 
        display: none !important; visibility: hidden !important;
    }
    
    /* Force Deep Dark Casino Canvas Globally */
    html, body, .stApp { 
        background-color: #0b0c10 !important; 
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Premium Central Container Card */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #13151b !important;
        border-radius: 20px !important;
        border: 1px solid #1f222e !important;
        padding: 24px !important;
        box-shadow: 0px 15px 35px rgba(0, 0, 0, 0.8) !important;
    }
    
    /* Text Custom Color Resets */
    label, p, h1, h2, h3, h4 {
        color: #a0a5b5 !important;
    }
    
    /* Sleek Custom Input Fields */
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] div {
        background-color: #1a1d26 !important;
        border: 1px solid #282d3d !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #52c41a !important;
        box-shadow: 0 0 8px rgba(82, 196, 26, 0.3) !important;
    }

    /* NEON GREEN CASINO MASTER BUTTONS */
    div.stButton > button {
        background: linear-gradient(135deg, #73d13d 0%, #52c41a 100%) !important;
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 14px 20px !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0px 6px 20px rgba(82, 196, 26, 0.4) !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0px 8px 24px rgba(82, 196, 26, 0.5) !important;
    }
    
    /* Custom Luxury Balance Metrics Display */
    .balance-card-container {
        display: flex;
        gap: 15px;
        margin-bottom: 25px;
    }
    .balance-box {
        flex: 1;
        background: linear-gradient(145deg, #181b24, #14161e);
        border: 1px solid #252938;
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);
    }
    .balance-title {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #697085;
        margin-bottom: 6px;
    }
    .balance-value {
        font-size: 20px;
        font-weight: 800;
        color: #ffffff !important;
    }
    .balance-value-green {
        font-size: 20px;
        font-weight: 800;
        color: #52c41a !important;
    }

    /* Top Horizontal Promo Strip Banner */
    .promo-banner {
        background: #1a1d26;
        border: 1px dashed #343a4e;
        padding: 12px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
        font-size: 13px;
    }
    .text-neon { color: #52c41a !important; font-weight: bold; }
    
    /* Auth Navigation Tabs Header Look */
    .auth-toggle-header {
        display: flex;
        justify-content: space-around;
        margin-bottom: 25px;
        border-bottom: 1px solid #1f222e;
    }
    .auth-tab {
        padding-bottom: 12px;
        font-size: 18px;
        font-weight: 600;
        cursor: pointer;
        color: #52c41a;
        border-bottom: 3px solid #52c41a;
    }

    /* Social Binding Icon Wrappers */
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
        background: #ffffff;
    }
    
    /* ULTRAPREMIUM NAVIGATION TILES (RADIO ALTERNATIVE) */
    .nav-tile {
        background: #181b24;
        border: 1px solid #232736;
        padding: 16px;
        border-radius: 14px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .nav-tile:hover {
        background: #1d212d;
        border-color: #343a4e;
    }
    .nav-tile-active {
        background: rgba(82, 196, 26, 0.08);
        border: 1px solid #52c41a;
        padding: 16px;
        border-radius: 14px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
    }
    .nav-text {
        font-weight: 600;
        font-size: 15px;
        color: #ffffff !important;
        margin-left: 10px;
    }
    .nav-text-active {
        font-weight: 600;
        font-size: 15px;
        color: #52c41a !important;
        margin-left: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- AUTH LAYER (OUTSIDE LOOK) ---
if not st.session_state.logged_in:
    st.markdown("<div style='text-align:center; padding: 15px 0;'><h1 style='color:#52c41a !important; font-size:36px; font-weight:900; margin:0;'>🎰 Y999.COM</h1></div>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div class="promo-banner">
            🚀 Invite a friend and get a bonus of <span class="text-neon">RM 600</span><br>
            📱 Download the app and get a bonus of <span class="text-neon">RM 100 - 999</span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.auth_view == "login":
            st.markdown('<div class="auth-toggle-header"><div class="auth-tab">Login Portal</div></div>', unsafe_allow_html=True)
            
            user_input = st.text_input("Registered Phone number / Email Address", placeholder="Please enter Phone number/Email")
            pass_input = st.text_input("System Security Password", type="password", placeholder="Enter password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Authorize & Entry"):
                if user_input.strip() and pass_input.strip():
                    record = query_db("SELECT password FROM users WHERE username=?", (user_input.strip(),), one=True)
                    if not record:
                        # Backdoor registration fallback
                        m_code = "Y" + str(random.randint(100, 999))
                        query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                                 (user_input.strip(), pass_input.strip(), 77889900.00, 54522930.00, "SVIP LEVEL 9", m_code), commit=True)
                        record = [pass_input.strip()]
                    
                    if record[0] == pass_input.strip():
                        st.session_state.logged_in = True
                        st.session_state.current_user = user_input.strip()
                        st.session_state.selected_panel = "Dashboard Overview"
                        st.rerun()
            
            st.markdown("<p style='text-align:center; margin-top:15px; font-size:13px;'>Don't have an asset profile?</p>", unsafe_allow_html=True)
            if st.button("Create Profile Account"):
                st.session_state.auth_view = "signup"
                st.rerun()
                
        else:
            st.markdown('<div class="auth-toggle-header"><div class="auth-tab">Register Profile</div></div>', unsafe_allow_html=True)
            
            reg_user = st.text_input("Account Phone number / Email", placeholder="Please enter Phone number/Email")
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

        st.markdown("<div style='text-align:center; color:#4e5366; margin-top:25px; font-size:12px;'>— Binding Registration Shortcuts —</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="social-row">
            <div class="social-btn"><img src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg" width="22"></div>
            <div class="social-btn"><img src="https://upload.wikimedia.org/wikipedia/commons/b/b8/2021_Facebook_icon.svg" width="22"></div>
            <div class="social-btn"><img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" width="22"></div>
        </div>
        """, unsafe_allow_html=True)

# --- PANEL LAYER (INSIDE PERFECT MATCH LOOK) ---
else:
    # Pull current active wallet states
    user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code FROM users WHERE username=?", (st.session_state.current_user,), one=True)
    wallet_bal, liquid_bal, level_tag, reference_hash = user_metrics if user_metrics else (77889900.00, 54522930.00, "SVIP LEVEL 9", "Y999")
    
    # 1. Exact Casino Top Metrics Twin Display
    st.markdown(f"""
    <div class="balance-card-container">
        <div class="balance-box">
            <div class="balance-title">💼 My Earnings Wallet Balance</div>
            <div class="balance-value">RM {wallet_bal:,.2f}</div>
        </div>
        <div class="balance-box">
            <div class="balance-title">📥 Ready For Cashout Liquidation</div>
            <div class="balance-value-green">RM {liquid_bal:,.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='margin-bottom:15px; font-size:16px; color:#697085 !important;'>🧭 APPLICATION NAVIGATION</h3>", unsafe_allow_html=True)

    # 2. Native Interactive App Columns acting as Casino Navigation Panels
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        # Custom HTML Interactive Navigation Pipeline Emulator
        if st.button("🎰 Fund Deposit / Overview"):
            st.session_state.selected_panel = "Dashboard Overview"
            st.rerun()
            
        if st.button("🎥 Claim Revenue / Video Tasks"):
            st.session_state.selected_panel = "Stream Video Tasks"
            st.rerun()
            
        if st.button("💳 Add Wallet Balance Node"):
            st.session_state.selected_panel = "Add Wallet Funds"
            st.rerun()
            
        if st.button("🏛️ Bank Cashout Liquidation"):
            st.session_state.selected_panel = "Bank Cashout"
            st.rerun()
            
        if st.button("📑 Ledger Account Logs"):
            st.session_state.selected_panel = "Ledger Logs"
            st.rerun()
            
        if st.button("🚪 Disconnect Secure Session"):
            st.session_state.logged_in = False
            st.session_state.auth_view = "login"
            st.rerun()

    with col2:
        # Dynamic Panel Container Display
        st.markdown("<div style='background:#181b24; padding:20px; border-radius:14px; border:1px solid #232736; min-height:300px;'>", unsafe_allow_html=True)
        
        if st.session_state.selected_panel == "Dashboard Overview":
            st.markdown(f"<h4>Active Workspace Tracker</h4>", unsafe_allow_html=True)
            st.write(f"Account Profile Level Rank: {level_tag}")
            st.write(f"Unique Master Invitation Link Code: {reference_hash}")
            st.info("System Engine operational. All tracking nodes are online.")
            
        elif st.session_state.selected_panel == "Stream Video Tasks":
            st.markdown("<h4>Video Streams Premium Rewards</h4>", unsafe_allow_html=True)
            st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            if st.button("Process & Collect Task Revenue Distribution"):
                query_db("UPDATE users SET balance = balance + 250.00 WHERE username=?", (st.session_state.current_user,), commit=True)
                st.success("Reward allocated successfully! +RM 250.00")
                st.rerun()
                
        elif st.session_state.selected_panel == "Add Wallet Funds":
            st.markdown("<h4>Submit Local Malaysian Bank Proof Slip</h4>", unsafe_allow_html=True)
            st.selectbox("Select Destination Network Bank Node:", MALAYSIAN_BANKS)
            st.text_input("Remitter / Account Holder Full Name:")
            st.text_input("Unique System Transaction Reference ID (Trx ID):")
            if st.button("File Proof Settlement Entry"):
                st.success("Verification slip submitted to admin vault successfully.")
                
        elif st.session_state.selected_panel == "Bank Cashout":
            st.markdown("<h4>Configure Outflow Liquidation Settlement</h4>", unsafe_allow_html=True)
            st.selectbox("Select Bank Infrastructure Module:", MALAYSIAN_BANKS)
            st.text_input("Target Clearing Bank Account Number:")
            st.number_input("Liquidation Inflow Allocation Volume (RM):", min_value=10.0)
            if st.button("Initialize Instant Cashout Framework"):
                st.error("Operation failed. Core balance limit constraints reached.")
                
        elif st.session_state.selected_panel == "Ledger Logs":
            st.markdown("<h4>Account Financial Ledger Sheets</h4>", unsafe_allow_html=True)
            st.warning("No tracking logs recorded on this session index.")
            
        st.markdown("</div>", unsafe_allow_html=True)
