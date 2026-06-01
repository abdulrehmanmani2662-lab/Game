import streamlit as st
import sqlite3
import pandas as pd
import random
import time

# Page Layout Configuration
st.set_page_config(page_title="Global Matrix Investment", page_icon="📈", layout="centered")

# --- DATABASE MANAGEMENT SUITE (SQLITE LAYER) ---
def init_db():
    conn = sqlite3.connect("matrix_vault.db", check_same_thread=False)
    cursor = conn.cursor()
    # Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            balance REAL,
            active_level TEXT,
            referred_by TEXT,
            ref_code TEXT,
            full_name TEXT,
            dob TEXT
        )
    """)
    # Deposits Table
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
    conn.commit()
    conn.close()

init_db()

def query_db(query, args=(), one=False, commit=False):
    conn = sqlite3.connect("matrix_vault.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(query, args)
    if commit:
        conn.commit()
        conn.close()
        return True
    rv = cursor.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

# --- PREMIUM VISUAL STYLESHEET ---
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;800&family=Poppins:wght@400;600;800&display=swap" rel="stylesheet">
    
    <style>
    header, footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stSidebar"] { 
        display: none !important; visibility: hidden !important;
    }
    .stApp { background-color: #030712 !important; }
    
    .main .block-container { 
        padding-top: 5px !important; 
        padding-bottom: 110px !important; 
        max-width: 430px !important;
        margin: 0 auto;
    }
    
    h1, h2, h3, h4, h5, h6, p, span, div, label, button, input {
        font-family: 'Poppins', sans-serif !important;
    }
    
    .ticker-wrap {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 12px; padding: 10px; text-align: center;
        margin-bottom: 15px; font-size: 12px; color: #f87171;
        font-weight: 600; letter-spacing: 0.5px;
    }

    label, [data-testid="stWidgetLabel"] p {
        color: #9ca3af !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        margin-bottom: 6px !important;
    }

    .stTextInput input, .stNumberInput input, .stDateInput input, div[data-baseweb="select"] {
        color: #ffffff !important;
        background-color: #0b0f19 !important;
        border: 1px solid #374151 !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }
    
    div[data-baseweb="select"] div {
        color: #ffffff !important;
        background-color: #0b0f19 !important;
    }
    
    .app-title-bar {
        text-align: center; font-size: 22px; color: #ffffff;
        font-family: 'Orbitron', sans-serif !important; font-weight: 800;
        letter-spacing: 2px; margin-bottom: 15px;
        background: linear-gradient(to right, #ef4444, #3b82f6);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    
    .balance-box {
        background: linear-gradient(135deg, #111827 0%, #030712 100%);
        padding: 25px; border-radius: 20px; border: 1px solid #1f2937;
        margin-bottom: 20px; text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }
    
    .section-label {
        font-size: 13px; color: #9ca3af; margin-top: 20px; margin-bottom: 10px; 
        font-weight: 600; letter-spacing: 1px; text-transform: uppercase;
    }
    
    .level-container {
        background: #111827; border: 1px solid #1f2937; border-radius: 14px;
        padding: 15px; margin-bottom: 12px;
    }

    .google-verification-card {
        background: #ffffff !important; color: #1f2937 !important;
        border-radius: 16px; padding: 25px; text-align: center; margin-bottom: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.4);
    }
    
    .invite-earn-box {
        background: #0b0f19; border: 1px dashed #ef4444; border-radius: 14px;
        padding: 15px; margin-top: 15px; text-align: center;
    }
    
    .payment-form-box {
        background: #111827; border: 1px solid #ef4444; border-radius: 16px;
        padding: 20px; margin-bottom: 20px;
    }
    
    .stButton>button {
        font-weight: 600 !important; font-size: 13px !important;
        border-radius: 10px !important; padding: 10px 0 !important;
        background: linear-gradient(90deg, #1f2937 0%, #111827 100%) !important;
        color: #ffffff !important; border: 1px solid #374151 !important;
    }
    .stButton>button:hover {
        border-color: #ef4444 !important;
        box-shadow: 0 0 10px rgba(239, 68, 68, 0.2) !important;
    }
    
    .action-btn-hub .stButton>button {
        background: linear-gradient(90deg, #ef4444 0%, #b91c1c 100%) !important;
        border: none !important;
    }
    
    .google-btn-hub .stButton>button {
        background: #ffffff !important;
        color: #1f2937 !important;
        border: 1px solid #dadce0 !important;
    }
    .google-btn-hub .stButton>button:hover {
        background: #f8f9fa !important;
        border-color: #c0c4c9 !important;
        box-shadow: 0 1px 3px rgba(60,64,67,0.3) !important;
    }

    .video-holder-box {
        background: #000000; border: 1px solid #1f2937; 
        border-radius: 14px; padding: 6px; margin-bottom: 15px;
    }
    
    .bottom-nav-holder {
        position: fixed; bottom: 0; left: 0; right: 0;
        background-color: #0b0f19; border-top: 1px solid #1f2937;
        padding: 12px 10px; z-index: 999999; max-width: 430px; margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)

LEVELS_CONF = {
    "VIP LEVEL 1": {"cost": 50, "daily_reward": 15},
    "VIP LEVEL 2": {"cost": 200, "daily_reward": 60},
    "VIP LEVEL 3": {"cost": 500, "daily_reward": 180}
}

# Session State Initialization
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'selected_payment_level' not in st.session_state: st.session_state.selected_payment_level = None
if 'google_screen_active' not in st.session_state: st.session_state.google_screen_active = False
if 'admin_video_url' not in st.session_state: st.session_state.admin_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
if 'current_app_tab' not in st.session_state: st.session_state.current_app_tab = "home"

# Email Verification States
if 'verification_stage' not in st.session_state: st.session_state.verification_stage = "closed"
if 'temp_register_data' not in st.session_state: st.session_state.temp_register_data = {}
if 'generated_otp' not in st.session_state: st.session_state.generated_otp = ""

query_params = st.query_params
if "ref" in query_params:
    st.session_state["saved_ref"] = query_params["ref"]
elif "saved_ref" not in st.session_state:
    st.session_state["saved_ref"] = "727"

# Real-Time Moving Feed Ticker
fake_users = ["ali_***", "mian_***", "tan_***", "lim_***", "raj_***", "zain_***"]
fake_actions = [
    f"just withdrew RM {random.randint(4,9)}00.00 successfully!",
    f"activated VIP LEVEL {random.randint(1,3)} node pipeline.",
    f"received RM 100.00 referral award incentive."
]
st.markdown(f'<div class="ticker-wrap">⚡ LIVE FEED: User {random.choice(fake_users)} {random.choice(fake_actions)}</div>', unsafe_allow_html=True)

st.markdown('<div class="app-title-bar">MATRIX PORTFOLIO</div>', unsafe_allow_html=True)

# --- STAGE 1: IDENTITY ACCESS HUBS ---
if not st.session_state.logged_in:
    
    # Track A: Google Official Identity Corridor
    if st.session_state.google_screen_active:
        st.markdown("""
        <div class="google-verification-card">
            <img src="https://fonts.gstatic.com/s/i/productlogos/googleg/v6/web-24dp/logo_googleg_color_24dp.png" width="36px" style="margin-bottom: 12px;"/>
            <h3 style="color:#202124; margin:0 0 8px 0; font-size:20px; font-weight:400;">Sign in</h3>
            <p style="color:#202124; font-size:14px; margin:0 0 25px 0;">to continue to Matrix Streamlit Protocol</p>
            
            <div style="border: 1px solid #dadce0; border-radius: 8px; padding: 12px; text-align: left; margin-bottom: 20px; display: flex; align-items: center; gap: 12px;">
                <div style="background: #ef4444; color: white; width: 32px; height: 32px; border-radius: 50%; text-align: center; line-height: 32px; font-weight: 600;">G</div>
                <div>
                    <div style="font-size: 13px; font-weight: 600; color: #3c4043;">salmanveerm@gmail.com</div>
                    <div style="font-size: 11px; color: #70757a;">Google Cloud Secured Session</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
        if st.button("CONFIRM AND SECURE SIGN IN", use_container_width=True):
            user_exists = query_db("SELECT * FROM users WHERE username=?", ("salmanveerm@gmail.com",), one=True)
            if not user_exists:
                query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", ("salmanveerm@gmail.com", 5.00, "None", st.session_state["saved_ref"], "2627", "Salman Veer", "1998-05-12"), commit=True)
            st.session_state.logged_in = True
            st.session_state.google_screen_active = False
            st.session_state.current_user = "salmanveerm@gmail.com"
            st.session_state.current_app_tab = "home"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
            
        if st.button("ABORT PROFILE SYNC", use_container_width=True):
            st.session_state.google_screen_active = False
            st.rerun()
            
    # Track B: Interactive OTP Verification Stage Frame
    elif st.session_state.verification_stage == "awaiting_otp":
        with st.form("otp_verification_form"):
            st.markdown(f"""
            <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; border-radius: 12px; padding: 15px; margin-bottom: 15px; text-align: center;">
                <p style="color: #60a5fa; font-size: 13px; margin: 0; font-weight: 600;">📧 VERIFICATION CODE DISPATCHED</p>
                <p style="color: #ffffff; font-size: 12px; margin: 4px 0 0 0;">A secure 6-digit verification sequence has been distributed to:<br><b style="color:#ef4444;">{st.session_state.temp_register_data['email']}</b></p>
            </div>
            """, unsafe_allow_html=True)
            
            user_otp_input = st.text_input("ENTER 6-DIGIT SECURITY CODE:", placeholder="••••••", max_chars=6)
            
            st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
            verify_submit = st.form_submit_button("VERIFY & INITIALIZE NODE", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if verify_submit:
                if user_otp_input.strip() == st.session_state.generated_otp:
                    t_data = st.session_state.temp_register_data
                    new_code = str(random.randint(1000, 9999))
                    
                    # Store safely in permanent SQLite ledger database
                    query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", 
                             (t_data['email'], 0.00, "None", st.session_state["saved_ref"], new_code, t_data['name'], str(t_data['dob'])), commit=True)
                    
                    st.session_state.logged_in = True
                    st.session_state.current_user = t_data['email']
                    st.session_state.verification_stage = "closed"
                    st.session_state.current_app_tab = "home"
                    st.success("Identity verified successfully!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Invalid passcode sequence! Please cross-check the distribution logs inside your email.")
                    
        if st.button("⬅ BACK TO MAIN REGISTRATION", use_container_width=True):
            st.session_state.verification_stage = "closed"
            st.rerun()

    # Track C: Primary Gateway Selector UI Frame
    else:
        st.markdown("<div style='text-align:center; padding:10px 0 20px 0;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 12px; color: #9ca3af; letter-spacing:1px; font-weight:600;'>SECURE NETWORK ACCESS</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Single Authorized OAuth Gateway
        st.markdown('<div class="google-btn-hub">', unsafe_allow_html=True)
        if st.button("🎯 CONTINUE WITH GOOGLE ACCOUNT", use_container_width=True):
            st.session_state.google_screen_active = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<p style='text-align:center; color:#4b5563; font-size:11px; margin: 25px 0;'>- OR CREATE DECENTRALIZED PLATFORM IDENTITY -</p>", unsafe_allow_html=True)
        
        # Manual Registration Track Form
        with st.form("manual_signup_form"):
            st.markdown("<p style='font-size:12px; color:#ffffff; font-weight:600; margin-bottom:10px;'>CREATE NEW INVESTMENT NODE</p>", unsafe_allow_html=True)
            reg_name = st.text_input("FULL NAME IDENTITY:", placeholder="John Doe")
            reg_email = st.text_input("EMAIL ADDRESS LOG:", placeholder="name@example.com")
            reg_dob = st.date_input("DATE OF BIRTH:")
            reg_admin_pass = st.text_input("ADMIN OVERRIDE KEY (OPTIONAL):", type="password", placeholder="Leave blank if registering as user")
            
            st.markdown('<div style="margin-top:15px;">', unsafe_allow_html=True)
            request_registration = st.form_submit_button("REQUEST ACCOUNT ACCOUNT PRIVILEGES", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if request_registration:
                u_email_clean = reg_email.strip()
                u_name_clean = reg_name.strip()
                
                if not u_email_clean or not u_name_clean:
                    st.error("Validation failed: Name and Email coordinates must be specified.")
                elif u_email_clean == "admin" or reg_admin_pass.strip() == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.session_state.current_user = "ADMIN_PANEL"
                    st.rerun()
                else:
                    # Check if node profile already exists in ledger history database
                    record_exists = query_db("SELECT * FROM users WHERE username=?", (u_email_clean,), one=True)
                    if record_exists:
                        # Existing user logs straight in to avoid duplicate bottlenecks
                        st.session_state.logged_in = True
                        st.session_state.current_user = u_email_clean
                        st.session_state.current_app_tab = "home"
                        st.rerun()
                    else:
                        # Create simulated email verification token payload
                        st.session_state.generated_otp = str(random.randint(100000, 999999))
                        st.session_state.temp_register_data = {
                            "name": u_name_clean,
                            "email": u_email_clean,
                            "dob": reg_dob
                        }
                        st.session_state.verification_stage = "awaiting_otp"
                        # Print code directly to terminal logs window for debugging
                        print(f"[SECURITY ALERT] VERIFICATION CODE FOR CODE DEPLOY: {st.session_state.generated_otp}")
                        st.rerun()

# --- STAGE 2: ADMINISTRATIVE CONTROLS DASHBOARD ---
elif st.session_state.logged_in and st.session_state.is_admin:
    st.markdown("<h4 style='color:#ef4444;'>👑 MASTER CONTROLLER PLATFORM LEDGER</h4>", unsafe_allow_html=True)
    
    st.session_state.admin_video_url = st.text_input("BROADCAST REWARD VIDEO TASK URL LINK:", value=st.session_state.admin_video_url)
    
    st.markdown('<div class="section-label">PENDING INBOUND ESCROW VERIFICATIONS</div>', unsafe_allow_html=True)
    reqs = query_db("SELECT * FROM deposits WHERE status='PENDING'")
    
    if not reqs:
        st.info("No transaction requests locked in memory cache frames.")
    else:
        for req in reqs:
            st.markdown(f"""
            <div class='level-container'>
                USER ID: {req[1]} | SUITE ASSIGNED: {req[2]}<br>
                SUM: <b>RM {req[3]}</b> | ROUTE SPEC: {req[4]}<br>
                HOLDER NAME: {req[5]} | TRX HASH BLOCK: <code>{req[6]}</code>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ UNLOCK PLAN", key=f"y_{req[0]}", use_container_width=True):
                    query_db("UPDATE users SET active_level=? WHERE username=?", (req[2], req[1]), commit=True)
                    query_db("UPDATE deposits SET status='APPROVED' WHERE id=?", (req[0],), commit=True)
                    
                    u_info = query_db("SELECT referred_by FROM users WHERE username=?", (req[1],), one=True)
                    if u_info and u_info[0]:
                        inviter = query_db("SELECT username FROM users WHERE ref_code=?", (u_info[0],), one=True)
                        if inviter:
                            bonus = 100.00 if req[3] == 200 else (50.00 if req[3] == 50 else 0)
                            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (bonus, inviter[0]), commit=True)
                    st.rerun()
            with c2:
                if st.button("❌ VOID PROOF", key=f"n_{req[0]}", use_container_width=True):
                    query_db("UPDATE deposits SET status='REJECTED' WHERE id=?", (req[0],), commit=True)
                    st.rerun()
                    
    if st.button("🚪 DISCONNECT CONTROL LAYER TERMINAL", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()

# --- STAGE 3: APPLICATION MAIN DASHBOARD INTERFACE ---
else:
    u_row = query_db("SELECT balance, active_level, ref_code, full_name FROM users WHERE username=?", (st.session_state.current_user,), one=True)
    curr_balance, curr_level, user_code, full_name = u_row[0], u_row[1], u_row[2], u_row[3]
    
    if st.session_state.current_app_tab == "home":
        st.markdown(f"""
        <div class="balance-box">
            <div style="color:#6b7280; font-size:11px; font-weight:500; letter-spacing:1px; margin-bottom:4px;">SECURE CORE NODE ID: {user_code}</div>
            <div style="color:#6b7280; font-size:12px; font-weight:500; margin-bottom:4px;">WELCOME BACK, <span style="color:#ffffff; font-weight:600;">{full_name}</span></div>
            <div style="color:#ef4444; font-size:11px; font-weight:600; letter-spacing:0.5px; text-transform:uppercase;">{curr_level} INFRASTRUCTURE MODULE STATUS</div>
            <div style="font-size:32px; font-family:'Orbitron', sans-serif !important; color:#ffffff; font-weight:800; margin-top:8px;">RM {curr_balance:.2f}</div>
            <div style="color:#9ca3af; font-size:12px; margin-top:2px;">NET LIQUID INVESTMENT ASSETS VALUATION</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Line Metric Chart Vector Rendering
        st.markdown('<div class="section-label">📉 REVENUE INDEX GROWTH PERFORMANCE</div>', unsafe_allow_html=True)
        chart_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Today"]
        chart_data = [curr_balance * 0.4, curr_balance * 0.5, curr_balance * 0.7, curr_balance * 0.8, curr_balance * 0.9, curr_balance * 0.95, curr_balance]
        df_metrics = pd.DataFrame({"Earning Matrix Line": chart_data}, index=chart_days)
        st.line_chart(df_metrics, y="Earning Matrix Line", color="#ef4444")

        c_dep, c_wdr = st.columns(2)
        with c_dep:
            if st.button("📥 LOAD ESCROW WALLET", use_container_width=True):
                st.info("Scroll down to standard Asset Portfolios and click initialize on target tier package row to open checkout panel.")
        with c_wdr:
            show_w = st.button("📤 WITHDRAW SYSTEM LIQUIDITY", use_container_width=True)
            
        if show_w:
            st.markdown("<div class='level-container'>", unsafe_allow_html=True)
            w_amt = st.number_input("TARGET WITHDRAW SUM CONTRACT VALUE (RM):", min_value=10, value=700)
            if st.button("🚀 REQUEST WITHDRAW SIGNAL PIPELINE", use_container_width=True):
                if w_amt < 700:
                    st.error("❌ PROTECTION BLOCK: SYSTEM SECURITY WITHDRAW LEVEL SET MINIMUM AT RM 700")
                elif curr_balance < w_amt:
                    st.error("❌ ESCROW FAILURE: COMPROMISED LEDGER BALANCE DUE TO FUND DEFICIT")
                else:
                    query_db("UPDATE users SET balance = balance - ? WHERE username=?", (w_amt, st.session_state.current_user), commit=True)
                    st.success("Withdraw authorization request transmitted to node verification matrix.")
                    time.sleep(1)
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # Checkout Allocation Form Window Block
        if st.session_state.selected_payment_level:
            lvl_name = st.session_state.selected_payment_level
            lvl_cost = LEVELS_CONF[lvl_name]["cost"]
            
            st.markdown('<div class="payment-form-box">', unsafe_allow_html=True)
            st.markdown(f"<p style='margin:0; text-align:center; color:#ffffff; font-size:14px; font-weight:600;'>SECURE ESCROW DEPOSIT GATEWAY CHECKOUT</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#9ca3af; text-align:center; font-size:12px; margin-bottom:15px;'>EVALUATION QUOTA COST TO SETTLE: <span style='color:#ef4444; font-weight:600;'>RM {lvl_cost}</span></p>", unsafe_allow_html=True)
            
            p_method = st.selectbox("CHOOSE TRANSMISSION NETWORK INTERFACE ROUTE:", ["Malaysia Local Bank", "Cryptocurrency (USDT TRC20)"])
            
            if p_method == "Malaysia Local Bank":
                t_bank = st.selectbox("SELECT INTERMEDIARY REGIONAL BANK COORDINATES:", [
                    "Maybank (Malayan Banking Berhad)", "CIMB Bank Berhad", "Public Bank Berhad", "RHB Bank Berhad", "Hong Leong Bank Berhad"
                ])
                st.markdown(f"""
                <div style="background:#0b0f19; border:1px solid #374151; padding:12px; border-radius:10px; margin-bottom:12px; font-size:12px; color:#ffffff;">
                    🏦 LOCAL BANK MATRIX DISTRIBUTION PARAMETERS:<br>
                    NAME: <b>GLOBAL ASSET CLEARING HOUSES LTD</b><br>
                    NUMBER NO: <code style='color:#ef4444;'>194058273645</code><br>
                    DESTINATION BANK NETWORK: <b>{t_bank}</b>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background:#0b0f19; border:1px solid #374151; padding:12px; border-radius:10px; margin-bottom:12px; font-size:12px; color:#ffffff;">
                    🌐 BLOCKCHAIN VAULT DATA ROUTE SEGMENT (USDT TRC20):<br>
                    BLOCK NETWORK LINK: <b>TRON ECOSYSTEM (TRC20 MAINNET)</b><br>
                    HASH ADDRESS ID: <code style='color:#10b981; word-break:break-all;'>TMatrix727SecureVaultCryptoPayloadSystemNode99X</code>
                </div>
                """, unsafe_allow_html=True)
                
            h_name = st.text_input("RECEIPT VERIFICATION REGISTERED ACCOUNT NAME:", placeholder="John Doe")
            t_id = st.text_input("NETWORK TRANSACTION INDEX HASH SEQUENCE (TRX ID):", placeholder="Enter transaction reference string")
            
            cb1, cb2 = st.columns(2)
            with cb1:
                st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
                submit_p = st.button("TRANSMIT PAYMENT PROOF FILE", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                if submit_p:
                    if h_name.strip() and t_id.strip():
                        query_db("INSERT INTO deposits (user, level, amount, method, holder_name, trx_id, status) VALUES (?, ?, ?, ?, ?, ?, 'PENDING')",
                                 (st.session_state.current_user, lvl_name, lvl_cost, p_method, h_name.strip(), t_id.strip()), commit=True)
                        st.success("Proof packet loaded successfully into transaction buffer queue!")
                        st.session_state.selected_payment_level = None
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Validation error: Identity records must be populated fully.")
            with cb2:
                if st.button("CANCEL TRANSACTION CHECKOUT", use_container_width=True):
                    st.session_state.selected_payment_level = None
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-label">💎 AVAILABLE INVESTMENT EXCLUSIVE SUITES</div>', unsafe_allow_html=True)
        for l_name, l_details in LEVELS_CONF.items():
            is_active = (curr_level == l_name)
            
            st.markdown(f"""
            <div class="level-container">
                <div style="font-size:14px; font-weight:600; color:#ffffff;">{l_name} <span style='color:#ef4444;'>{"[ACTIVE ALLOCATION CONTRACT]" if is_active else ""}</span></div>
                <div style="color:#9ca3af; font-size:11px; margin-top:2px;">DAILY SPONSORED STREAM TASK RETURN: <span style="color:#ef4444; font-weight:600;">RM {l_details['daily_reward']:.2f}</span></div>
                <div style="color:#9ca3af; font-size:11px;">MINIMUM ACQUISITION CAPITAL VALUATION: <span style="color:#ffffff; font-weight:600;">RM {l_details['cost']}</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            if is_active:
                st.button(f"🚀 SYSTEM NODE {l_name} CAPTURING PAYOUTS", key=f"ac_{l_name}", disabled=True, use_container_width=True)
            else:
                if st.button(f"⚡ INITIALIZE ACQUISITION FOR {l_name}", key=f"un_{l_name}", use_container_width=True):
                    if curr_balance >= l_details['cost']:
                        query_db("UPDATE users SET balance = balance - ?, active_level=? WHERE username=?", (l_details['cost'], l_name, st.session_state.current_user), commit=True)
                        st.success(f"System node contract {l_name} initiated successfully!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.session_state.selected_payment_level = l_name
                        st.warning("Earning parameters data limit exceeded! Loading checkouts form window frame.")
                        time.sleep(0.5)
                        st.rerun()

        st.markdown(f"""
        <div class="invite-earn-box">
            <div style="font-size:13px; color:#ef4444; font-weight:600; letter-spacing:0.5px;">🤝 INVITE AFFILIATE PARALLEL ASSOCIATES</div>
            <div style="font-size:11px; color:#9ca3af; margin-bottom:8px;">DISTRIBUTE UNIQUE CLUSTER SEED SEED NODE LINK AND REAP HIGHER BONUSES</div>
            <div style="background:#030712; border:1px solid #1f2937; border-radius:8px; padding:8px; font-size:11px; color:#f87171; font-family:monospace !important; word-break: break-all;">
                https://money.streamlit.app/?ref={user_code}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ------------------ TAB ROUTER: TASK PIPELINES ------------------
    elif st.session_state.current_app_tab == "task":
        st.markdown("<p style='text-align:center; color:#9ca3af; font-size:12px;'>MEDIA BROADCAST ADVERTISING REWARD PATH</p>", unsafe_allow_html=True)
        
        task_payout = 5.00 if curr_level == "None" else float(LEVELS_CONF[curr_level]["daily_reward"])
        
        st.markdown(f"""
        <div class='level-container' style='text-align:center;'>
            <p style='margin:0; font-size:12px; color:#9ca3af;'>TIER RUNTIME ENGAGEMENT EARNING VALUE: <b style='color:#ef4444; font-size:14px;'>RM {task_payout:.2f}</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="video-holder-box">', unsafe_allow_html=True)
        st.video(st.session_state.admin_video_url)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
        claim_btn = st.button("CONSOLIDATE LIVE STREAM CONVERSION REWARDS", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if claim_btn:
            with st.spinner("⏳ COMPUTING SYSTEM ANALYTICS LOG ENGAGEMENT WITH EDGE BLOCK..."):
                time.sleep(2.5)
            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (task_payout, st.session_state.current_user), commit=True)
            st.toast(f"Ledger balance array state synchronized verified: +RM {task_payout:.2f}", icon="💰")
            time.sleep(0.5)
            st.session_state.current_app_tab = "home"
            st.rerun()

    # --- THREE BUTTONS STATIC ROW HUD INTERFACE FOOTER NAVIGATION ---
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown('<div class="bottom-nav-holder">', unsafe_allow_html=True)
    col_nav1, col_nav2, col_nav3 = st.columns(3)
    with col_nav1:
        if st.button("🏠 PORTFOLIO", key="n_hm", use_container_width=True):
            st.session_state.current_app_tab = "home"
            st.session_state.selected_payment_level = None
            st.rerun()
    with col_nav2:
        if st.button("📺 STREAM", key="n_tk", use_container_width=True):
            st.session_state.current_app_tab = "task"
            st.rerun()
    with col_nav3:
        if st.button("🚪 TERMINATE", key="n_lo", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = ""
            st.session_state.selected_payment_level = None
            st.session_state.current_app_tab = "home"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
