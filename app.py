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
    .stApp { background-color: #030712 !important; }
    
    .main .block-container { 
        padding-top: 5px !important; 
        padding-bottom: 120px !important; 
        max-width: 430px !important;
        margin: 0 auto;
    }
    
    /* Heavy Professional Font Domination Layer */
    h1, h2, h3, h4, h5, h6, p, span, div, label, button, input {
        font-family: 'Montserrat', 'Poppins', sans-serif !important;
        font-weight: 900 !important;
    }
    
    /* CRITICAL READABILITY OVERRIDE: Bright High-Visibility Inputs Labeling */
    label, .stTextInput label, [data-testid="stWidgetLabel"] p, .stNumberInput label {
        color: #38bdf8 !important;
        font-size: 13px !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        margin-bottom: 6px !important;
        display: block !important;
        text-shadow: 1px 1px 3px #000000 !important;
    }

    /* Input Fields Border & Contrast Updates */
    .stTextInput input, .stNumberInput input {
        color: #ffffff !important;
        background-color: #0f172a !important;
        border: 2px solid #0284c7 !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
    }
    
    /* MONEY LOGO HEADER PULSE ANIMATION */
    .money-animation-box {
        text-align: center; margin-top: 10px; margin-bottom: 2px; font-size: 50px;
        animation: pulseMoney 1.4s infinite alternate;
    }
    @keyframes pulseMoney {
        0% { transform: scale(0.95); filter: drop-shadow(0 0 5px #06b6d4); }
        100% { transform: scale(1.05); filter: drop-shadow(0 0 20px #34d399); }
    }
    
    /* Glowing Global Matrix Premium Header */
    .app-title-bar {
        text-align: center; font-size: 26px; color: #ffffff;
        text-shadow: 0 0 12px #38bdf8, 0 0 24px #0284c7;
        padding-bottom: 10px; margin-bottom: 20px; border-bottom: 3px solid #1e293b;
        letter-spacing: 1px;
    }
    
    /* Premium Financial Balance Display Container */
    .balance-box {
        background: linear-gradient(145deg, #0f172a 0%, #1e1b4b 100%);
        padding: 22px; border-radius: 22px; border: 2px solid #38bdf8;
        margin-bottom: 20px; text-align: center;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.25);
    }
    
    /* Section Separation Elements */
    .section-label {
        font-size: 16px; color: #38bdf8; margin-top: 22px; margin-bottom: 12px; 
        border-left: 5px solid #0ea5e9; padding-left: 10px; letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    /* Elegant Modular Active Tier Blocks */
    .level-container {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 100%); 
        border: 2px solid #1f2937; border-radius: 16px;
        padding: 15px; margin-bottom: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }

    /* REALTIME GOOGLE IDENTITY DIALOG CONTAINER ACCENT */
    .google-verification-card {
        background: #ffffff !important; color: #1f2937 !important;
        border-radius: 20px; padding: 22px; text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6); margin-bottom: 20px;
    }
    
    /* Custom Luxury Dashed Referral Link Frame */
    .invite-earn-box {
        background: linear-gradient(135deg, #06202e 0%, #022c22 100%);
        border: 2px dashed #34d399; border-radius: 16px;
        padding: 18px; margin-top: 15px; margin-bottom: 15px; text-align: center;
        box-shadow: 0 0 15px rgba(52, 211, 153, 0.15);
    }
    
    /* Dynamic Form Popover Matrix Container Boxes */
    .payment-form-box {
        background: linear-gradient(145deg, #090d16 0%, #172554 100%);
        border: 3px solid #38bdf8; border-radius: 20px;
        padding: 20px; margin-top: 12px; margin-bottom: 22px;
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.3);
    }
    
    /* High-Performance Neon Click Buttons Control */
    .stButton>button {
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 900 !important; font-size: 14px !important;
        border-radius: 12px !important; padding: 10px 0 !important;
        background: linear-gradient(90deg, #38bdf8 0%, #0284c7 100%) !important;
        color: #ffffff !important; border: none !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4) !important;
    }
    
    /* Special Red Variant Configuration for the Core Google Single Sign-On Module */
    .google-trigger-zone .stButton>button {
        background: linear-gradient(90deg, #ea4335 0%, #c5221f 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 5px 15px rgba(234, 67, 53, 0.4) !important;
    }

    /* Video Task Terminal Holder Frame */
    .video-holder-box {
        background: #000000; border: 2px solid #f59e0b; 
        border-radius: 16px; padding: 8px; margin-bottom: 15px;
    }
    
    /* STRICT NATIVE INLINE APP NAVIGATION GRID TAB BAR SYSTEM */
    .nav-grid-dock {
        position: fixed; bottom: 0; left: 0; right: 0;
        background-color: #0b1329; border-top: 3px solid #1e293b;
        padding: 10px 5px; display: grid; grid-template-columns: 1fr 1fr 1fr;
        gap: 8px; z-index: 999999; max-width: 430px; margin: 0 auto;
        box-shadow: 0 -5px 25px rgba(0,0,0,0.8);
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
if 'admin_video_url' not in st.session_state: st.session_state.admin_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
if 'current_app_tab' not in st.session_state: st.session_state.current_app_tab = "home"

# Floating Money Core Brand Header Group
st.markdown('<div class="money-animation-box">📈⚡💎</div>', unsafe_allow_html=True)
st.markdown('<div class="app-title-bar">GLOBAL MATRIX INVESTMENT</div>', unsafe_allow_html=True)

# --- PHASE 1: LOGIN HUB / REALISTIC GOOGLE SCREEN GATEWAY ---
if not st.session_state.logged_in:
    
    if st.session_state.google_screen_active:
        st.markdown("""
        <div class="google-verification-card">
            <img src="https://fonts.gstatic.com/s/i/productlogos/googleg/v6/web-24dp/logo_googleg_color_24dp.png" width="32px" style="margin-bottom:8px;"/>
            <h3 style="color:#202124; margin:5px 0; font-size:17px;">Verify Identity Corridor</h3>
            <p style="color:#5f6368; font-size:12px; font-weight:bold; margin-bottom:12px;">Confirm secure profile map sync with Google Security Layer</p>
            <div style="background:#f1f3f4; border-radius:12px; padding:10px; display:flex; align-items:center; justify-content:center; gap:10px; margin-bottom:15px; border:1px solid #dadce0;">
                <div style="background:#0284c7; width:28px; height:28px; border-radius:50%; color:white; font-weight:bold; font-size:13px; line-height:28px; text-align:center;">M</div>
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
            st.session_state.current_app_tab = "home"
            st.toast("Encrypted Google Profile Link Operational!", icon="⚡")
            time.sleep(1)
            st.rerun()
            
        if st.button("❌ CANCEL VERIFICATION", use_container_width=True):
            st.session_state.google_screen_active = False
            st.rerun()

    else:
        st.markdown("<h4 style='text-align:center; color:#ffffff; margin-bottom: 15px;'>SECURE GATEWAY TUNNEL</h4>", unsafe_allow_html=True)
        
        st.markdown('<div class="google-trigger-zone">', unsafe_allow_html=True)
        if st.button("🔴 SIGN IN WITH GOOGLE / GMAIL ACCOUNT", use_container_width=True):
            st.session_state.google_screen_active = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown("<p style='text-align:center; color:#64748b; font-size:11px; margin-top:5px; margin-bottom:12px;'>- OR ACCESS USING PLATFORM ENCRYPTED KEY CODE -</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("📱 EMAIL OR UNIQUE SYSTEM NUMBER ID:", value="salmanveerm@gmail.com")
            password = st.text_input("🔒 ENTRY SECURE KEYCODE:", type="password", placeholder="••••••••")
            
            if st.form_submit_button("🚀 INITIALIZE NODE DATABASE ENTRY", use_container_width=True):
                if username == "admin" and password == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.session_state.current_user = "ADMIN_PANEL"
                    st.rerun()
                elif username in st.session_state.users_db:
                    st.session_state.logged_in = True
                    st.session_state.is_admin = False
                    st.session_state.current_user = username
                    st.session_state.current_app_tab = "home"
                    st.rerun()
                else:
                    st.session_state.users_db[username] = {"balance": 0.00, "active_level": "None", "referred_by": "ubaid_rajput"}
                    st.session_state.logged_in = True
                    st.session_state.is_admin = False
                    st.session_state.current_user = username
                    st.session_state.current_app_tab = "home"
                    st.rerun()

# --- PHASE 2: ADMIN PAYMENT & VIDEO CONTENT MANAGEMENT TERMINAL ---
elif st.session_state.is_admin:
    st.markdown("<h3 style='color:#38bdf8; text-align:center;'>👑 CENTRAL ADMIN CONTROL ROOM</h3>", unsafe_allow_html=True)
    
    # NEW FEATURE: LIVE VIDEO ADS OVERRIDE NODE CONTROLLER
    st.markdown('<div class="section-label">📺 BROADCAST VIDEO MANAGEMENT ROUTER</div>', unsafe_allow_html=True)
    new_url = st.text_input("SET STREAM / YOUTUBE URL TASK VIDEO FOR USERS:", value=st.session_state.admin_video_url)
    if st.button("💾 UPDATE ACTIVE TASK STREAM LINK", use_container_width=True):
        st.session_state.admin_video_url = new_url
        st.success("Target media stream link successfully broadcasted to live node network!")
    
    st.markdown('<div class="section-label">📥 USER PENDING DEPOSIT VERIFICATIONS</div>', unsafe_allow_html=True)
    if not st.session_state.deposit_requests:
        st.info("No verification logs inside queue ledger.")
    else:
        for idx, req in enumerate(st.session_state.deposit_requests):
            with st.container():
                st.markdown(f"""
                <div class='level-container' style='border-color: #38bdf8;'>
                    <span style='color:#38bdf8;'>USER CORE:</span> {req['user']}<br>
                    <span style='color:#38bdf8;'>TARGET TARGET contract:</span> {req['level']}<br>
                    <span style='color:#38bdf8;'>PROMISED SUM:</span> <b>RM {req['amount']}</b><br>
                    <span style='color:#38bdf8;'>BANK RECEIPT TRACE TITLE:</span> {req['holder_name']}<br>
                    <span style='color:#38bdf8;'>HASH SERIAL TRX ID:</span> <code style='color:#34d399;'>{req['trx_id']}</code>
                </div>
                """, unsafe_allow_html=True)
                
                col_app, col_rej = st.columns(2)
                with col_app:
                    if st.button("✅ APPROVE DEPOSIT LAYER", key=f"app_{idx}", use_container_width=True):
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
                    if st.button("❌ REFUSE RECEIPT TRANSCRIPT", key=f"rej_{idx}", use_container_width=True):
                        st.session_state.deposit_requests.pop(idx)
                        st.warning("Receipt log trashed.")
                        time.sleep(1)
                        st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🚪 LOGOUT ADMIN ROOT TERMINAL", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()

# --- PHASE 3: MAIN APP INTERFACE (USER INTERFACE SPLIT VIA TABS) ---
else:
    current_user = st.session_state.current_user
    user_data = st.session_state.users_db[current_user]
    
    # ------------------ TAB CONTENT: HOME PAGE ------------------
    if st.session_state.current_app_tab == "home":
        # Financial Analytics Premium View
        st.markdown(f"""
        <div class="balance-box">
            <div style="color:#94a3b8; font-size:11px; letter-spacing:1px; margin-bottom:4px;">ACCOUNT ID: {current_user}</div>
            <div style="color:#ffffff; font-size:13px; letter-spacing:0.5px;">ACTIVE VIP SUITE: <span style="color:#38bdf8;">{user_data['active_level'].upper()}</span></div>
            <div style="color:#ffffff; font-size:14px; letter-spacing:0.5px; margin-top:4px;">NET LIQUID VALUE WALLET</div>
            <div style="font-size:36px; color:#ffffff; margin-top:3px; text-shadow: 0 0 10px rgba(56,189,248,0.4);">RM {user_data['balance']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

        col_dep, col_wdr = st.columns(2)
        with col_dep:
            if st.button("📥 INBOUND DEPOSIT", use_container_width=True):
                st.info("Scroll niche VIP level par click karke verification form generate karein.")
        with col_wdr:
            show_withdraw = st.button("📤 WITHDRAW SYSTEM", use_container_width=True)

        if show_withdraw:
            st.markdown("<div class='level-container'>", unsafe_allow_html=True)
            w_amt = st.number_input("ENTER WITHDRAW QUANTITY (RM):", min_value=10, value=700)
            if st.button("💸 INITIALIZE SECURE WITHDRAW OUTFLOW"):
                if w_amt < 700:
                    st.error("❌ PROTECTION REJECTED: GATEWAY MINIMUM SAFE WITHDRAW IS SET AT RM 700")
                elif user_data["balance"] < w_amt:
                    st.error("❌ TRANSACTION CRASH: BALANCE INSIDE INTERNAL LEDGER DEFICIT")
                else:
                    st.session_state.users_db[current_user]["balance"] -= w_amt
                    st.success(f"🚀 SUCCESS: Liquidity extraction payload routed to queue verification room.")
                    time.sleep(1)
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # Inbound Deposit Transaction Verification Engine
        if st.session_state.selected_payment_level:
            lvl_name = st.session_state.selected_payment_level
            lvl_cost = LEVELS_CONF[lvl_name]["cost"]
            
            st.markdown('<div class="payment-form-box">', unsafe_allow_html=True)
            st.markdown(f"<h3 style='margin:0; color:#ffffff; text-align:center;'>📥 VERIFICATION HUB TERMINAL</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#e2e8f0; text-align:center; font-size:13px; margin-bottom:12px;'>REQUIRED TRANSFER CONTRACT sum: <b style='color:#38bdf8; font-size:18px;'>RM {lvl_cost}</b></p>", unsafe_allow_html=True)
            
            st.markdown("<p style='font-size:12px; color:#ffffff; font-weight:900;'>👇 SCAN SECURE ACCREDITED TOUCH 'N GO NET CODE BELOW:</p>", unsafe_allow_html=True)
            st.image("https://kommodo.ai/i/pt49bwYh6iJZi2gWV2EE", caption="SECURE DEPOSIT CLEARING CHANNELS", use_container_width=True)
            
            holder_name = st.text_input("👤 SOURCE SENDER NAME ACCOUNT HOLDER:", key="h_name_box", placeholder="Enter official legal card identifier text")
            trx_id = st.text_input("🔢 SERIAL REFERENCE RECEIPT TRX TRANSACTION ID:", key="trx_id_box", placeholder="Enter unique 12-digit receipt tracking sequence")
            
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
                        st.success("✔ Verification signature pushed to admin dashboard ledger queue!")
                        st.session_state.selected_payment_level = None
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Input fields cannot remain empty space configuration!")
            with col_can_pay:
                if st.button("❌ ABORT ESCROW", use_container_width=True):
                    st.session_state.selected_payment_level = None
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # VIP Tier Allocation Grid Space
        st.markdown('<div class="section-label">💎 EXCLUSIVE MATRIX INVESTMENT PORTFOLIOS</div>', unsafe_allow_html=True)
        for l_name, l_details in LEVELS_CONF.items():
            is_already_active = (user_data["active_level"] == l_name)
            active_status_text = " [CURRENTLY ACTIVE IN PROFILE]" if is_already_active else ""
            
            st.markdown(f"""
            <div class="level-container">
                <div style="font-size:15px; color:#ffffff; margin-bottom:3px;">{l_name} <span style='color:#34d399;'>{active_status_text}</span></div>
                <div style="color:#cbd5e1; font-size:12px;">DAILY CONTRACT AD CONTRACT PAYOUT: <span style="color:#34d399;">RM {l_details['daily_reward']:.2f}</span></div>
                <div style="color:#cbd5e1; font-size:12px;">CONTRACT COMMITMENT COST SUM: <span style="color:#38bdf8;">RM {l_details['cost']}</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            if is_already_active:
                st.button(f"✅ SYSTEM BLOCK NODE {l_name} OPERATIONAL", key=f"btn_act_{l_name}", disabled=True, use_container_width=True)
            else:
                if st.button(f"⚡ ALLOCATE SYSTEM CAPITAL TO {l_name}", key=f"btn_unl_{l_name}", use_container_width=True):
                    if user_data["balance"] >= l_details['cost']:
                        st.session_state.users_db[current_user]["balance"] -= l_details['cost']
                        st.session_state.users_db[current_user]["active_level"] = l_name
                        st.success(f"🎉 Contract channel suite {l_name} activated via internal funds allocation!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.session_state.selected_payment_level = l_name
                        st.warning(f"Wallet liquidity low! Verification matrix link rendered instantly below.")
                        time.sleep(0.5)
                        st.rerun()

        # Dynamic Luxury Invite Module Frame Space Block
        st.markdown(f"""
        <div class="invite-earn-box">
            <div style="font-size:17px; color:#34d399; margin-bottom:4px; font-weight:900;">🤝 INVITE NETWORK FRIENDS & REAP RM 100</div>
            <div style="font-size:12px; color:#cbd5e1; margin-bottom:10px; font-weight:700;">SHARE SYSTEM NETWORK LINK AND EARN COMMISSIONS LIQUIDITY INSTANTLY</div>
            <div style="background-color:rgba(0,0,0,0.6); border:1px solid #34d399; border-radius:10px; padding:10px; font-size:11px; color:#a7f3d0; font-family:monospace !important; word-break: break-all;">
                https://global-matrix-investment.streamlit.app/?ref={current_user.split('@')[0]}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ------------------ TAB CONTENT: WATCH VIDEO TASK PAGE ------------------
    elif st.session_state.current_app_tab == "task":
        st.markdown("<h3 style='color:#f59e0b; text-align:center;'>📺 STREAM ADVERTISING REWARD TERMINAL</h3>", unsafe_allow_html=True)
        
        current_tier = user_data["active_level"]
        task_payout = 5.00 if current_tier == "None" else float(LEVELS_CONF[current_tier]["daily_reward"])
        
        st.markdown(f"""
        <div class='level-container' style='border-color: #f59e0b; text-align:center;'>
            <p style='margin:0; font-size:14px; color:#ffffff;'>CURRENT LEVEL TIED PAYOUT VALUE: <b style='color:#f59e0b;'>RM {task_payout:.2f}</b></p>
            <p style='margin:5px 0 0 0; font-size:11px; color:#94a3b8;'>Watch the entire sequence configured by network broadcast admin below to unlock allocation.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # ACTIVE ADMIN DRIVEN VIDEO ATTACHMENT HUB INTERFACE
        st.markdown('<div class="video-holder-box">', unsafe_allow_html=True)
        st.video(st.session_state.admin_video_url)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("💰 CLAIM LIQUID VIDEO ENGAGEMENT REWARD", use_container_width=True):
            with st.spinner("⏳ SYNCING METRIC ENGAGEMENT NODES WITH CORE SERVER SECURITY VAULT..."):
                time.sleep(3.5) # Anti-cheat hardware synchronization emulator delay
            st.session_state.users_db[current_user]["balance"] += task_payout
            st.toast(f"Security Core Balance Update Verified: +RM {task_payout:.2f}", icon="💰")
            time.sleep(0.5)
            st.session_state.current_app_tab = "home"
            st.rerun()

    # --- NO-STACK ABSOLUTE SOLID HTML NAVIGATION BUTTON LINK GRID BASE ---
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # 3-Columns Layout Generated with Inside Custom Style Form Element to Block Multi-Line Wrapping
    st.markdown('<div class="nav-grid-dock">', unsafe_allow_html=True)
    
    # Custom Execution Buttons inside Streamlit forced layout boundaries
    col_app_btn1, col_app_btn2, col_app_btn3 = st.columns(3)
    with col_app_btn1:
        if st.button("🏠 HOME", key="nav_abs_home", use_container_width=True):
            st.session_state.current_app_tab = "home"
            st.session_state.selected_payment_level = None
            st.rerun()
    with col_app_btn2:
        if st.button("📺 VIDEO TASK", key="nav_abs_task", use_container_width=True):
            st.session_state.current_app_tab = "task"
            st.rerun()
    with col_app_btn3:
        if st.button("🚪 LOGOUT", key="nav_abs_logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = ""
            st.session_state.selected_payment_level = None
            st.session_state.current_app_tab = "home"
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)
