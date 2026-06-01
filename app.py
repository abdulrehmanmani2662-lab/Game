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
            ref_code TEXT
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
    # Insert default data if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users VALUES ('salmanveerm@gmail.com', 5.00, 'None', '727', '2627')")
        cursor.execute("INSERT INTO users VALUES ('ubaid_rajput', 50.00, 'None', '', '727')")
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

# --- PREMIUM VISUAL STYLESHEET (REAL FINANCIAL SYSTEM LOOK) ---
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
    
    /* Live Moving Live Ticker Style */
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

    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] {
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
        border-radius: 16px; padding: 20px; text-align: center; margin-bottom: 20px;
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

# Session State Synchronization
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'selected_payment_level' not in st.session_state: st.session_state.selected_payment_level = None
if 'google_screen_active' not in st.session_state: st.session_state.google_screen_active = False
if 'admin_video_url' not in st.session_state: st.session_state.admin_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
if 'current_app_tab' not in st.session_state: st.session_state.current_app_tab = "home"

query_params = st.query_params
if "ref" in query_params:
    st.session_state["saved_ref"] = query_params["ref"]
elif "saved_ref" not in st.session_state:
    st.session_state["saved_ref"] = "727"

# Real-Time Moving Feed Simulator
fake_users = ["ali_***", "mian_***", "tan_***", "lim_***", "raj_***", "zain_***"]
fake_actions = [
    f"just withdrew RM {random.randint(4,9)}00.00 successfully!",
    f"activated VIP LEVEL {random.randint(1,3)} node pipeline.",
    f"received RM 100.00 referral award incentive."
]
st.markdown(f'<div class="ticker-wrap">⚡ LIVE LOG: User {random.choice(fake_users)} {random.choice(fake_actions)}</div>', unsafe_allow_html=True)

st.markdown('<div class="app-title-bar">MATRIX PORTFOLIO</div>', unsafe_allow_html=True)

# --- STAGE 1: SYSTEM SECURITY PORTAL ---
if not st.session_state.logged_in:
    if st.session_state.google_screen_active:
        st.markdown("""
        <div class="google-verification-card">
            <img src="https://fonts.gstatic.com/s/i/productlogos/googleg/v6/web-24dp/logo_googleg_color_24dp.png" width="28px"/>
            <h3 style="color:#202124; margin:10px 0 5px 0; font-size:16px; font-weight:600;">Sign in with Google</h3>
            <p style="color:#5f6368; font-size:12px; margin-bottom:15px;">to continue to Matrix secure cloud network mapping</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔒 AUTHORIZE VIA GOOGLE ACCOUNT", use_container_width=True):
            user_exists = query_db("SELECT * FROM users WHERE username=?", ("salmanveerm@gmail.com",), one=True)
            if not user_exists:
                query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?)", ("salmanveerm@gmail.com", 5.00, "None", st.session_state["saved_ref"], "2627"), commit=True)
            st.session_state.logged_in = True
            st.session_state.google_screen_active = False
            st.session_state.current_user = "salmanveerm@gmail.com"
            st.session_state.current_app_tab = "home"
            st.rerun()
            
        if st.button("❌ CANCEL ACCESS", use_container_width=True):
            st.session_state.google_screen_active = False
            st.rerun()
    else:
        with st.form("secure_login"):
            st.markdown("<p style='text-align:center; font-size:12px; color:#9ca3af;'>SECURE IDENTITY GATEWAY</p>", unsafe_allow_html=True)
            username = st.text_input("USER LOGIN ID (EMAIL OR ACCOUNT ID):", placeholder="name@example.com")
            password = st.text_input("SECURE PASSPHRASE KEYCODE:", type="password", placeholder="••••••••")
            
            if st.form_submit_button("ENTER ACCOUNT MATRIX", use_container_width=True):
                u_clean = username.strip()
                p_clean = password.strip()
                
                if not u_clean or not p_clean:
                    st.error("Fields cannot remain empty space string layouts.")
                elif u_clean == "admin" and p_clean == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.session_state.current_user = "ADMIN_PANEL"
                    st.rerun()
                else:
                    user_row = query_db("SELECT * FROM users WHERE username=?", (u_clean,), one=True)
                    if user_row:
                        st.session_state.logged_in = True
                        st.session_state.current_user = u_clean
                    else:
                        new_code = str(random.randint(1000, 9999))
                        query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (u_clean, 0.00, "None", st.session_state["saved_ref"], new_code), commit=True)
                        st.session_state.logged_in = True
                        st.session_state.current_user = u_clean
                    st.session_state.current_app_tab = "home"
                    st.rerun()
                    
        st.markdown("<p style='text-align:center; color:#4b5563; font-size:11px;'>- OR ALTERNATIVE ACCESS INTERFACE -</p>", unsafe_allow_html=True)
        if st.button("🔴 OAUTH FAST SECURE SIGN IN", use_container_width=True):
            st.session_state.google_screen_active = True
            st.rerun()

# --- STAGE 2: ADMIN CENTRAL COMMAND PANEL ---
elif st.session_state.logged_in and st.session_state.is_admin:
    st.markdown("<h4 style='color:#ef4444;'>👑 ADMINISTRATIVE LEDGER ROOM</h4>", unsafe_allow_html=True)
    
    st.session_state.admin_video_url = st.text_input("BROADCAST REWARD STREAM LINK:", value=st.session_state.admin_video_url)
    
    st.markdown('<div class="section-label">PENDING INBOUND ESCROW DEPOSITS</div>', unsafe_allow_html=True)
    reqs = query_db("SELECT * FROM deposits WHERE status='PENDING'")
    
    if not reqs:
        st.info("No logs present inside ledger memory stack.")
    else:
        for req in reqs:
            st.markdown(f"""
            <div class='level-container'>
                USER: {req[1]} | CONTRACT: {req[2]}<br>
                SUM: <b>RM {req[3]}</b> | METHOD: {req[4]}<br>
                TITLE: {req[5]} | TRX HASH: <code>{req[6]}</code>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ APPROVE", key=f"y_{req[0]}", use_container_width=True):
                    query_db("UPDATE users SET active_level=? WHERE username=?", (req[2], req[1]), commit=True)
                    query_db("UPDATE deposits SET status='APPROVED' WHERE id=?", (req[0],), commit=True)
                    
                    # Process referral payouts
                    u_info = query_db("SELECT referred_by FROM users WHERE username=?", (req[1],), one=True)
                    if u_info and u_info[0]:
                        inviter = query_db("SELECT username FROM users WHERE ref_code=?", (u_info[0],), one=True)
                        if inviter:
                            bonus = 100.00 if req[3] == 200 else (50.00 if req[3] == 50 else 0)
                            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (bonus, inviter[0]), commit=True)
                    st.rerun()
            with c2:
                if st.button("❌ REJECT", key=f"n_{req[0]}", use_container_width=True):
                    query_db("UPDATE deposits SET status='REJECTED' WHERE id=?", (req[0],), commit=True)
                    st.rerun()
                    
    if st.button("🚪 LEAVE TERMINAL CONTROL", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()

# --- STAGE 3: ACCOUNT REAL DASHBOARD INTERFACE ---
else:
    u_row = query_db("SELECT balance, active_level, ref_code FROM users WHERE username=?", (st.session_state.current_user,), one=True)
    curr_balance, curr_level, user_code = u_row[0], u_row[1], u_row[2]
    
    if st.session_state.current_app_tab == "home":
        st.markdown(f"""
        <div class="balance-box">
            <div style="color:#6b7280; font-size:11px; font-weight:500; letter-spacing:1px; margin-bottom:4px;">ACCOUNT SECURE ID: {user_code}</div>
            <div style="color:#ef4444; font-size:12px; font-weight:600; letter-spacing:0.5px; text-transform:uppercase;">{curr_level} SUBSCRIPTION TIED</div>
            <div style="font-size:32px; font-family:'Orbitron', sans-serif !important; color:#ffffff; font-weight:800; margin-top:8px;">RM {curr_balance:.2f}</div>
            <div style="color:#9ca3af; font-size:12px; margin-top:2px;">NET FINANCIAL ASSETS CAPITAL</div>
        </div>
        """, unsafe_allow_html=True)
        
        # --- PREMIUM METRIC LINE CHART GRAPH (REALISTIC FINANCIAL VIBE) ---
        st.markdown('<div class="section-label">📉 CAPITAL REVENUE PERFORMANCE TIMELINE</div>', unsafe_allow_html=True)
        chart_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Today"]
        chart_data = [curr_balance * 0.4, curr_balance * 0.5, curr_balance * 0.7, curr_balance * 0.8, curr_balance * 0.9, curr_balance * 0.95, curr_balance]
        df_metrics = pd.DataFrame({"Timeline Data": chart_data}, index=chart_days)
        st.line_chart(df_metrics, y="Timeline Data", color="#ef4444")

        c_dep, c_wdr = st.columns(2)
        with c_dep:
            if st.button("📥 INBOUND FUNDING", use_container_width=True):
                st.info("Neeche scroll karein aur jis VIP Matrix Asset ko buy karna hai us par click karke form activate karein.")
        with c_wdr:
            show_w = st.button("📤 EXTRACT LIQUIDITY", use_container_width=True)
            
        if show_w:
            st.markdown("<div class='level-container'>", unsafe_allow_html=True)
            w_amt = st.number_input("EXTRACTION TARGET AMOUNT (RM):", min_value=10, value=700)
            if st.button("⚡ EXECUTE ESCROW WITHDRAW ROUTE", use_container_width=True):
                if w_amt < 700:
                    st.error("❌ ROUTER REJECTION: MINIMUM SYSTEM WITHDRAW RESTRICTION SET AT RM 700")
                elif curr_balance < w_amt:
                    st.error("❌ FINANCIAL CRISIS: INSUFFICIENT BALANCE IN CURRENT VAULT TIMELINE")
                else:
                    query_db("UPDATE users SET balance = balance - ? WHERE username=?", (w_amt, st.session_state.current_user), commit=True)
                    st.success("Extraction signature recorded. Waiting admin network release block.")
                    time.sleep(1)
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # --- FUNDING INTERFACE FLOW FORM PANEL ---
        if st.session_state.selected_payment_level:
            lvl_name = st.session_state.selected_payment_level
            lvl_cost = LEVELS_CONF[lvl_name]["cost"]
            
            st.markdown('<div class="payment-form-box">', unsafe_allow_html=True)
            st.markdown(f"<p style='margin:0; text-align:center; color:#ffffff; font-size:15px; font-weight:600;'>SECURE CONTRACT CHECKOUT VIA NODE</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#9ca3af; text-align:center; font-size:12px; margin-bottom:15px;'>FUNDS NEEDED FOR ACTIVATION: <span style='color:#ef4444; font-weight:600;'>RM {lvl_cost}</span></p>", unsafe_allow_html=True)
            
            p_method = st.selectbox("NETWORK PAYMENT SPECIFICATION CHANNELS:", ["Malaysia Local Bank", "Cryptocurrency (USDT TRC20)"])
            
            if p_method == "Malaysia Local Bank":
                t_bank = st.selectbox("CHOOSE SYSTEM INTERMEDIARY BANK:", [
                    "Maybank (Malayan Banking Berhad)", "CIMB Bank Berhad", "Public Bank Berhad", "RHB Bank Berhad", "Hong Leong Bank Berhad"
                ])
                st.markdown(f"""
                <div style="background:#0b0f19; border:1px solid #374151; padding:12px; border-radius:10px; margin-bottom:12px; font-size:12px; color:#ffffff;">
                    🏦 BANK ROUTING WIRE MATRIX TARGET:<br>
                    NAME: <b>GLOBAL ESCROW CAPITAL LIMITED</b><br>
                    NUMBER: <code style='color:#ef4444;'>194058273645</code><br>
                    BANK SELECTION ROUTE: <b>{t_bank}</b>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background:#0b0f19; border:1px solid #374151; padding:12px; border-radius:10px; margin-bottom:12px; font-size:12px; color:#ffffff;">
                    🌐 BLOCKCHAIN ADDRESS TARGET SEQUENCE (USDT TRC20):<br>
                    NETWORK: <b>TRON (TRC20 LAYER LINK)</b><br>
                    ADDRESS: <code style='color:#10b981; word-break:break-all;'>TMatrix727SecureVaultCryptoPayloadSystemNode99X</code>
                </div>
                """, unsafe_allow_html=True)
                
            h_name = st.text_input("ACCOUNT OWNER RECEIPT TEXT MATCH TITLE:", placeholder="John Doe")
            t_id = st.text_input("SYSTEM SEQUENCE HASH REFERENCE (TRX ID):", placeholder="12-digit transaction index sequence")
            
            cb1, cb2 = st.columns(2)
            with cb1:
                st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
                submit_p = st.button("🔥 SEND SECURE PROOF", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                if submit_p:
                    if h_name.strip() and t_id.strip():
                        query_db("INSERT INTO deposits (user, level, amount, method, holder_name, trx_id, status) VALUES (?, ?, ?, ?, ?, ?, 'PENDING')",
                                 (st.session_state.current_user, lvl_name, lvl_cost, p_method, h_name.strip(), t_id.strip()), commit=True)
                        st.success("Proof uploaded to persistence matrix database!")
                        st.session_state.selected_payment_level = None
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Input rows require matching structure inputs.")
            with cb2:
                if st.button("❌ ABORT TRANSITION", use_container_width=True):
                    st.session_state.selected_payment_level = None
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-label">💎 EXCLUSIVE ASSET MATRIX PORTFOLIOS</div>', unsafe_allow_html=True)
        for l_name, l_details in LEVELS_CONF.items():
            is_active = (curr_level == l_name)
            
            st.markdown(f"""
            <div class="level-container">
                <div style="font-size:14px; font-weight:600; color:#ffffff;">{l_name} <span style='color:#ef4444;'>{"[ACTIVE SYSTEM CONTRACT]" if is_active else ""}</span></div>
                <div style="color:#9ca3af; font-size:11px; margin-top:2px;">DAILY AD STREAM PAYOUT REWARD VALUE: <span style="color:#ef4444; font-weight:600;">RM {l_details['daily_reward']:.2f}</span></div>
                <div style="color:#9ca3af; font-size:11px;">ACQUISITION THRESHOLD VALUE: <span style="color:#ffffff; font-weight:600;">RM {l_details['cost']}</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            if is_active:
                st.button(f"🚀 {l_name} CAPTURING LIVE TIERS", key=f"ac_{l_name}", disabled=True, use_container_width=True)
            else:
                if st.button(f"⚡ INITIALIZE ACQUISITION FOR {l_name}", key=f"un_{l_name}", use_container_width=True):
                    if curr_balance >= l_details['cost']:
                        query_db("UPDATE users SET balance = balance - ?, active_level=? WHERE username=?", (l_details['cost'], l_name, st.session_state.current_user), commit=True)
                        st.success("Matrix cluster tier allocated successfully.")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.session_state.selected_payment_level = l_name
                        st.warning("Earning parameters deficient! Fund acquisition form launched inside dashboard viewport below.")
                        time.sleep(0.5)
                        st.rerun()

        st.markdown(f"""
        <div class="invite-earn-box">
            <div style="font-size:14px; color:#ef4444; font-weight:600; letter-spacing:0.5px;">🤝 DEPLOY INTERMEDIARY COMMISSIONS LINK</div>
            <div style="font-size:11px; color:#9ca3af; margin-bottom:8px;">SHARE YOUR SEED TOKEN NODE AND REAP RM 100 BONUS STRUCTURE</div>
            <div style="background:#030712; border:1px solid #1f2937; border-radius:8px; padding:8px; font-size:11px; color:#f87171; font-family:monospace !important; word-break: break-all;">
                https://money.streamlit.app/?ref={user_code}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ------------------ TAB ROUTER: STREAM AD SYSTEM ------------------
    elif st.session_state.current_app_tab == "task":
        st.markdown("<p style='text-align:center; color:#9ca3af; font-size:12px;'>DATA ADVERTISING CHANNEL STREAM</p>", unsafe_allow_html=True)
        
        task_payout = 5.00 if curr_level == "None" else float(LEVELS_CONF[curr_level]["daily_reward"])
        
        st.markdown(f"""
        <div class='level-container' style='text-align:center;'>
            <p style='margin:0; font-size:12px; color:#9ca3af;'>TIER CONTRACT RETURN RATE: <b style='color:#ef4444; font-size:14px;'>RM {task_payout:.2f}</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="video-holder-box">', unsafe_allow_html=True)
        st.video(st.session_state.admin_video_url)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
        claim_btn = st.button("💰 CONSOLIDATE EARNED ASSET YIELD", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if claim_btn:
            with st.spinner("⏳ SYNCING METRIC DATA INTEGRATION PACKETS WITH CLOUD ESCROW..."):
                time.sleep(2)
            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (task_payout, st.session_state.current_user), commit=True)
            st.toast(f"Ledger account state synchronized: +RM {task_payout:.2f}", icon="💰")
            time.sleep(0.5)
            st.session_state.current_app_tab = "home"
            st.rerun()

    # --- FOOTER BUTTON NAVIGATION HUB ROW CONTAINER ---
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
        if st.button("🚪 HALT", key="n_lo", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = ""
            st.session_state.selected_payment_level = None
            st.session_state.current_app_tab = "home"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
