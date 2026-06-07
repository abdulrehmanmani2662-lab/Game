import streamlit as st
import sqlite3
import random

# Core App Layout Configuration
st.set_page_config(page_title="GLOBAL NETWORK MATRIX", page_icon="📈", layout="wide")

MALAYSIAN_BANKS = [
    "Touch 'n Go eWallet",
    "Maybank (Malayan Banking Berhad)",
    "CIMB Bank Berhad",
    "Public Bank Berhad",
    "RHB Bank Berhad",
    "Hong Leong Bank Berhad"
]

# --- SECURE STABLE DATABASE INTERFACE ---
def init_db():
    conn = sqlite3.connect("matrix_vault.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY, password TEXT, balance REAL, liquidation REAL, active_level TEXT, ref_code TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_config (
            key TEXT PRIMARY KEY, value TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, bank TEXT, name TEXT, trx_id TEXT, amount REAL, status TEXT
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO system_config VALUES ('live_ad_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ')")
    cursor.execute("INSERT OR IGNORE INTO system_config VALUES ('tng_scanner_url', 'https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg')")
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'admin123', 0.0, 0.0, 'OWNER', 'MASTER')")
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

# --- SESSION STATES ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'selected_panel' not in st.session_state: st.session_state.selected_panel = "Overview"
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = "Login"
if 'reset_step' not in st.session_state: st.session_state.reset_step = 1

# --- SYSTEM DESIGN SYSTEM (FIXED TEXT VISIBILITY & NEON OVERRIDES) ---
st.markdown("""
    <style>
    /* Hide Streamlit Native Footers and Top Bars */
    footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stHeader"] { 
        display: none !important; visibility: hidden !important;
    }
    
    /* Background - Premium Dark Cyber Punk Vibe */
    html, body, .stApp { 
        background: linear-gradient(rgba(11, 9, 26, 0.95), rgba(6, 4, 15, 0.98)), 
                    url("https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?q=80&w=1470&auto=format&fit=crop") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* 🌈 ANIMATED RGB COLOR STRIP FIXED ON TOP */
    .rgb-moving-strip {
        height: 8px;
        width: 100%;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 99999;
        background: linear-gradient(90deg, #ff0055, #00ffcc, #ff00aa, #00ff55, #ffcc00, #ff0055);
        background-size: 400% 400%;
        animation: rgb-strip-move 6s linear infinite;
    }
    @keyframes rgb-strip-move {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Typography Upgrades - Mote Aur Wazni Fonts */
    h1, h2, h3, h4, p, label, .stMarkdown {
        font-weight: 800 !important;
    }
    
    .brand-title {
        text-align: center;
        font-size: 32px;
        font-weight: 900 !important;
        letter-spacing: 1px;
        background: linear-gradient(135deg, #ffffff 40%, #00ffcc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 30px;
        margin-bottom: 20px;
        text-transform: uppercase;
    }

    /* Input Fields Customization */
    div[data-testid="stTextInput"] input, 
    div[data-testid="stNumberInput"] input, 
    div[data-testid="stSelectbox"] div {
        background-color: #1a172e !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 1px solid #3c3761 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 12px !important;
    }
    
    /* --- UNIVERSAL STRONG BUTTON DESIGN (NO MORE BLANK WHITE BLOCKS) --- */
    div[data-testid="stButton"] > button {
        width: 100% !important;
        display: block !important;
        font-weight: 900 !important;
        font-size: 16px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 20px !important;
        margin-top: 5px !important;
        margin-bottom: 5px !important;
        transition: all 0.2s ease-in-out;
    }

    /* Explicit Text Visibility Overrides */
    div[data-testid="stButton"] > button p {
        color: #ffffff !important;
        font-weight: 900 !important;
    }

    /* Individual Custom Color Logic Without Overlapping Containers */
    div.btn-cyan div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
        box-shadow: 0px 4px 15px rgba(0, 242, 254, 0.4) !important;
    }
    div.btn-cyan div[data-testid="stButton"] > button p { color: #000000 !important; }
    
    div.btn-gold div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%) !important;
        box-shadow: 0px 4px 15px rgba(246, 211, 101, 0.4) !important;
    }
    div.btn-gold div[data-testid="stButton"] > button p { color: #000000 !important; }
    
    div.btn-pink div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #f857a6 0%, #ff5858 100%) !important;
        box-shadow: 0px 4px 15px rgba(248, 87, 166, 0.4) !important;
    }
    
    div.btn-green div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%) !important;
        box-shadow: 0px 4px 15px rgba(0, 176, 155, 0.4) !important;
    }

    div.btn-violet div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #7f00ff 0%, #e100ff 100%) !important;
        box-shadow: 0px 4px 15px rgba(127, 0, 255, 0.4) !important;
    }
    
    div.btn-red div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%) !important;
        box-shadow: 0px 4px 15px rgba(255, 65, 108, 0.4) !important;
    }
    
    div[data-testid="stButton"] > button:hover {
        transform: scale(1.02) !important;
        filter: brightness(1.15) !important;
    }

    /* Metrics Visual Cards Display Block */
    .metric-card-box {
        background: linear-gradient(135deg, rgba(32, 28, 59, 0.95) 0%, rgba(20, 17, 38, 0.95) 100%);
        border-left: 6px solid #00ffcc;
        border-radius: 12px;
        padding: 25px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0px 10px 25px rgba(0,0,0,0.4);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="rgb-moving-strip"></div>', unsafe_allow_html=True)

def switch_panel(panel_name):
    st.session_state.selected_panel = panel_name
    st.rerun()

# --- GATEWAY MANAGEMENT RENDER LAYER ---
if not st.session_state.logged_in:
    st.markdown('<div class="brand-title">👑 GLOBAL MATRIX INVESTMENT</div>', unsafe_allow_html=True)
    
    if st.session_state.auth_mode == "Login":
        username = st.text_input("Registered Account Email / Username:", placeholder="e.g. user@gmail.com")
        password = st.text_input("System Security Password:", type="password", placeholder="••••••••")
        
        st.markdown('<div class="btn-cyan">', unsafe_allow_html=True)
        if st.button("Authorize Secure Access"):
            if username.strip() == "admin":
                record = query_db("SELECT password FROM users WHERE username='admin'", one=True)
                if record and record[0] == password.strip():
                    st.session_state.logged_in = True
                    st.session_state.current_user = "admin"
                    st.session_state.is_admin = True
                    st.session_state.selected_panel = "Pending Requests"
                    st.rerun()
                else:
                    st.error("Credentials pairing failed database matching.")
            elif username.strip():
                record = query_db("SELECT password, username FROM users WHERE username=?", (username.strip(),), one=True)
                if record and record[0] == password.strip():
                    st.session_state.logged_in = True
                    st.session_state.current_user = record[1]
                    st.session_state.is_admin = False
                    st.session_state.selected_panel = "Overview"
                    st.rerun()
                else:
                    st.error("Credentials pairing failed database matching.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="btn-gold">', unsafe_allow_html=True)
        if st.button("Create Profile Account"):
            st.session_state.auth_mode = "Register"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="btn-violet">', unsafe_allow_html=True)
        if st.button("Forgot Security Password?"):
            st.session_state.auth_mode = "Forgot"
            st.session_state.reset_step = 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.auth_mode == "Register":
        st.markdown("<h4 style='color:#00ffcc;'>Initialize New Registry Node</h4>", unsafe_allow_html=True)
        reg_username = st.text_input("Provide Profile Registration Email Key:")
        reg_password = st.text_input("Establish System Security Code:", type="password")
        
        st.markdown('<div class="btn-green">', unsafe_allow_html=True)
        if st.button("Deploy Account Node Parameters"):
            if reg_username.strip() and reg_password.strip():
                existing = query_db("SELECT username FROM users WHERE username=?", (reg_username.strip(),), one=True)
                if existing:
                    st.error("Identity keys collision: Data values already exist inside vault.")
                else:
                    query_db("INSERT INTO users VALUES (?, ?, 0.00, 0.00, 'SVIP LEVEL 9', 'Y999')", 
                             (reg_username.strip(), reg_password.strip()), commit=True)
                    st.success("Allocation logged. Proceed to connect authorization node.")
                    st.session_state.auth_mode = "Login"
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="btn-red">', unsafe_allow_html=True)
        if st.button("Return to Log In Hub"):
            st.session_state.auth_mode = "Login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.auth_mode == "Forgot":
        st.markdown("<h4 style='color:#00ffcc;'>System Access Key Recovery Matrix</h4>", unsafe_allow_html=True)
        
        if st.session_state.reset_step == 1:
            f_email = st.text_input("Enter Registered Identification Email:")
            st.markdown('<div class="btn-cyan">', unsafe_allow_html=True)
            if st.button("Search Master Vault Nodes"):
                user_match = query_db("SELECT username FROM users WHERE username=?", (f_email.strip(),), one=True)
                if user_match:
                    st.session_state.reset_email = f_email.strip()
                    st.session_state.generated_code = str(random.randint(111111, 999999))
                    st.session_state.reset_step = 2
                    st.rerun()
                else:
                    st.error("No account parameters verified for current string inputs.")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="btn-red">', unsafe_allow_html=True)
            if st.button("Cancel Operation"):
                st.session_state.auth_mode = "Login"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
                    
        elif st.session_state.reset_step == 2:
            st.info(f"🔒 Security token initialized for route: {st.session_state.reset_email}")
            st.warning(f"Development Sync Override Code: {st.session_state.generated_code}")
            
            input_code = st.text_input("Enter 6-Digit Verification Pin:")
            new_pass = st.text_input("Define Replacement Security Password Target:", type="password")
            
            st.markdown('<div class="btn-green">', unsafe_allow_html=True)
            if st.button("Re-commit Credentials Lock"):
                if input_code.strip() == st.session_state.generated_code:
                    if len(new_pass.strip()) >= 4:
                        query_db("UPDATE users SET password=? WHERE username=?", (new_pass.strip(), st.session_state.reset_email), commit=True)
                        st.success("Vault passwords restructured cleanly.")
                        st.session_state.auth_mode = "Login"
                        st.session_state.reset_step = 1
                        st.rerun()
                    else:
                        st.error("String block index length parameters invalid.")
                else:
                    st.error("Security token pairing logic invalid.")
            st.markdown('</div>', unsafe_allow_html=True)

# --- APPLICATION DESKTOP INTERFACE RENDER LAYER ---
else:
    if st.session_state.is_admin:
        st.markdown("<h3 style='color:#00ffcc; font-weight:900; margin-top:15px; text-align:center;'>🛡️ MASTER ENGINE ADMINISTRATION</h3>", unsafe_allow_html=True)
        
        st.markdown('<div class="btn-cyan">', unsafe_allow_html=True)
        if st.button("📥 Action Deposits Pipeline Channels"): switch_panel("Pending Requests")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="btn-pink">', unsafe_allow_html=True)
        if st.button("🔗 Modify Task URL Targets"): switch_panel("Edit Task Redirects")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="btn-violet">', unsafe_allow_html=True)
        if st.button("🖼️ Re-align Terminal TNG Scanner Asset"): switch_panel("Edit QR Source")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="btn-red">', unsafe_allow_html=True)
        if st.button("🚪 Terminate Global Core Admin Session"):
            st.session_state.logged_in = False
            st.session_state.is_admin = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.write("---")
        
        if st.session_state.selected_panel == "Pending Requests":
            st.markdown("<h4 style='color:#00ffcc;'>Inflow Ledger Verification Channels</h4>", unsafe_allow_html=True)
            pending_items = query_db("SELECT id, username, bank, name, trx_id, amount FROM deposits WHERE status='Pending'")
            
            if not pending_items:
                st.info("Validation processing logs queue is completely clear.")
            else:
                for item in pending_items:
                    with st.container():
                        st.markdown(f"""
                        <div style='background-color:#1c1836; padding:18px; border-radius:10px; border-left:5px solid #ff0055; margin-bottom:15px;'>
                            <p style='margin:3px 0;'><b>Node Profile User Key:</b> {item[1]}</p>
                            <p style='margin:3px 0;'><b>Wire Route Destination:</b> {item[2]} ({item[3]})</p>
                            <p style='margin:3px 0; color:#ffcc00;'><b>Asset Transaction Hash:</b> {item[4]}</p>
                            <h3 style='color:#00ffcc; margin:5px 0 0 0;'>Claim Volumetric: RM {item[5]:.2f}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown('<div class="btn-green">', unsafe_allow_html=True)
                        if st.button(f"Approve Inflow RM {item[5]:.2f}", key=f"adm_app_{item[0]}"):
                            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (item[5], item[1]), commit=True)
                            query_db("UPDATE deposits SET status='Approved' WHERE id=?", (item[0],), commit=True)
                            st.success("Allocations updated inside node core.")
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown('<div class="btn-red">', unsafe_allow_html=True)
                        if st.button(f"Drop / Purge Request Record", key=f"adm_rej_{item[0]}"):
                            query_db("UPDATE deposits SET status='Rejected' WHERE id=?", (item[0],), commit=True)
                            st.error("Log record purged successfully.")
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                                
        elif st.session_state.selected_panel == "Edit Task Redirects":
            st.markdown("<h4 style='color:#4facfe;'>System Redirection Parameters Configuration</h4>", unsafe_allow_html=True)
            current_ad_url = query_db("SELECT value FROM system_config WHERE key='live_ad_url'", one=True)
            url_str = current_ad_url[0] if current_ad_url else ""
            
            new_url = st.text_input("Active System Redirection URL Location Config:", value=url_str)
            st.markdown('<div class="btn-pink">', unsafe_allow_html=True)
            if st.button("Deploy New Target Redirect Path"):
                query_db("UPDATE system_config SET value=? WHERE key='live_ad_url'", (new_url.strip(),), commit=True)
                st.success("Matrix redirection structures recompiled successfully.")
            st.markdown('</div>', unsafe_allow_html=True)
                
        elif st.session_state.selected_panel == "Edit QR Source":
            st.markdown("<h4 style='color:#e100ff;'>Touch 'n Go Payment Scanner Asset Mapping</h4>", unsafe_allow_html=True)
            current_qr_url = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)
            qr_str = current_qr_url[0] if current_qr_url else ""
            
            new_qr = st.text_input("Direct URL Link of New QR Image:", value=qr_str)
            st.markdown('<div class="btn-violet">', unsafe_allow_html=True)
            if st.button("Synchronize Terminal Scanner Display Map"):
                query_db("UPDATE system_config SET value=? WHERE key='tng_scanner_url'", (new_qr.strip(),), commit=True)
                st.success("Target payment scanner terminals system synchronization complete.")
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        wallet_bal, liquid_bal, level_tag, reference_hash = user_metrics if user_metrics else (0.00, 0.00, "SVIP LEVEL 9", "Y999")
        
        st.markdown(f"""
        <div class="metric-card-box">
            <p style="font-size:12px; color:#a5a1c2; margin:0; letter-spacing:1px; font-weight:800;">MY EARNINGS WALLET BALANCE (Dompet Perolehan Saya)</p>
            <h1 style="font-size:38px; font-weight:900; color:#00ffcc; margin:5px 0;">RM {wallet_bal:,.2f}</h1>
            <p style="font-size:13px; color:#ffffff; margin:0; font-weight:700;">READY FOR IMMEDIATE CASHOUT LIQUIDATION: <span style='color:#ff0055;'>RM {liquid_bal:,.2f}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="btn-cyan">', unsafe_allow_html=True)
        if st.button("📊 System Tracking Metrics Overview"): switch_panel("Overview")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="btn-gold">', unsafe_allow_html=True)
        if st.button("💰 Add Dompet Account System Funds"): switch_panel("Deposit")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="btn-green">', unsafe_allow_html=True)
        if st.button("🏛️ Cashout Settlement Clearing Protocol"): switch_panel("Cashout")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="btn-red">', unsafe_allow_html=True)
        if st.button("🚪 Disconnect Portal System Access Link"): 
            st.session_state.logged_in = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.write("---")
        
        if st.session_state.selected_panel == "Overview":
            st.markdown("<h4 style='color:#00f2fe;'>Operational Allocation Metrics</h4>", unsafe_allow_html=True)
            st.write(f"Verification Infrastructure Matrix Rank: **{level_tag}**")
            st.write(f"Active Allocation Invitation Reference: **{reference_hash}**")
            
            ad_link_data = query_db("SELECT value FROM system_config WHERE key='live_ad_url'", one=True)
            target_video = ad_link_data[0] if ad_link_data else "#"
            
            st.markdown(f"""
            <div style='background-color:#1a1730; padding:20px; border-radius:12px; border: 1px solid rgba(0, 242, 254, 0.3); margin-top:15px; width:100%;'>
                <h4 style='margin:0 0 5px 0; color:#ffffff;'>YOUTUBE & MEDIA REVENUE STREAM PIPELINE</h4>
                <p style='font-size:13px; color:#a5a1c2; margin-bottom:15px;'>Interact with data tasking stream nodes to instantly trigger internal rewards system payouts.</p>
                <a href='{target_video}' target='_blank' style='display:block; text-align:center; background: linear-gradient(135deg, #f857a6 0%, #ff5858 100%); color:#ffffff; padding:14px; text-decoration:none; font-weight:800; border-radius:10px; box-shadow:0 4px 15px rgba(248,87,166,0.35);'>▶️ LAUNCH ACTIVE VIDEO TASK NODE</a>
            </div>
            """, unsafe_allow_html=True)
            
        elif st.session_state.selected_panel == "Deposit":
            st.markdown("<h4 style='color:#f6d365;'>Multi-Bank Payload Inflow Via Touch 'n Go</h4>", unsafe_allow_html=True)
            
            qr_link_data = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)
            target_qr = qr_link_data[0] if qr_link_data else ""
            
            if target_qr:
                st.markdown(f"<div style='text-align:center; margin-bottom:20px;'><img src='{target_qr}' width='190' style='border:3px solid #f6d365; border-radius:12px; background:white; padding:5px;'/></div>", unsafe_allow_html=True)
            
            chosen_bank = st.selectbox("Select Target Banking Inflow Node:", MALAYSIAN_BANKS)
            remitter_name = st.text_input("Sender Remitter / Registrant Account Name:")
            trx_id_input = st.text_input("System Reference Ref-ID / Trx Transaction Number:")
            amount_input = st.number_input("Inflow Valuation Volume Amount (RM):", min_value=1.0, value=10.0)
            
            st.markdown('<div class="btn-gold">', unsafe_allow_html=True)
            if st.button("Execute Submission Dispatch Logs"):
                if remitter_name.strip() and trx_id_input.strip():
                    query_db("INSERT INTO deposits (username, bank, name, trx_id, amount, status) VALUES (?, ?, ?, ?, ?, 'Pending')",
                             (st.session_state.current_user, chosen_bank, remitter_name.strip(), trx_id_input.strip(), amount_input), commit=True)
                    st.success("Evidence logs stacked into system clearing verification queue.")
                else:
                    st.error("Submission Input Criteria Incomplete. Please fill all fields.")
            st.markdown('</div>', unsafe_allow_html=True)
                    
        elif st.session_state.selected_panel == "Cashout":
            st.markdown("<h4 style='color:#00b09b;'>Initialize Outbound Settlement Pipeline</h4>", unsafe_allow_html=True)
            st.selectbox("Select Destination Network Clearance Bank Node:", MALAYSIAN_BANKS[1:])
            st.text_input("Receiver Account Wire Index Account Number Key:")
            st.number_input("Target Settlement Request Dimensions (RM):", min_value=10.0)
            
            st.markdown('<div class="btn-green">', unsafe_allow_html=True)
            if st.button("Authorize Outbound Terminal Cashout Dispatch"):
                st.error("Operation Halted: Target database node balance maps out of context index parameters.")
            st.markdown('</div>', unsafe_allow_html=True)
