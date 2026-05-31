import streamlit as st
import time

# Page Layout Configuration
st.set_page_config(page_title="Global Matrix Investment", page_icon="📈", layout="centered")

# --- PREMIUM NEXUS GAMING LOOK & BOLD LABELS STYLESHEET ---
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700;900&family=Poppins:wght@700;900&display=swap" rel="stylesheet">
    
    <style>
    header, footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stSidebar"] { 
        display: none !important; visibility: hidden !important;
    }
    .stApp { background-color: #060913 !important; }
    
    .main .block-container { 
        padding-top: 15px !important; 
        padding-bottom: 100px !important; 
        max-width: 440px !important;
        margin: 0 auto;
    }
    
    /* Global Typography Reset to Ultra-Bold */
    h1, h2, h3, h4, h5, h6, p, span, div, label, button, input {
        font-family: 'Montserrat', 'Poppins', sans-serif !important;
        font-weight: 900 !important;
    }
    
    /* CRITICAL FIX: Custom Forced Styles for Form Visibility & High Contrast Labels */
    label, .stTextInput label, [data-testid="stWidgetLabel"] p, .stNumberInput label {
        color: #ffffff !important;
        font-size: 14px !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.7px !important;
        margin-bottom: 8px !important;
        display: block !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    }
    
    /* Title Top Neon Branding Header */
    .app-title-bar {
        text-align: center; font-size: 25px; color: #fff;
        text-shadow: 0 0 10px #f59e0b, 0 0 20px #f59e0b;
        padding: 15px 10px; margin-bottom: 20px; border-bottom: 2px solid #1e293b;
        letter-spacing: 1.5px;
    }
    
    /* Premium Crypto Wallet Box */
    .balance-box {
        background: linear-gradient(145deg, #111827 0%, #030712 100%);
        padding: 22px; border-radius: 18px; border: 2px solid #f59e0b;
        margin-bottom: 20px; text-align: center;
        box-shadow: 0 0 15px rgba(245, 158, 11, 0.3);
    }
    
    /* Section Sidebar Visual Anchors */
    .section-label {
        font-size: 18px; color: #f59e0b; margin-top: 25px; margin-bottom: 12px; 
        border-left: 6px solid #f59e0b; padding-left: 12px; letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    /* Unified Structural Card Grid Modules */
    .level-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); 
        border: 2px solid #334155; border-radius: 15px;
        padding: 16px; margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }

    /* Referral Program Box System styling */
    .invite-earn-box {
        background: linear-gradient(135deg, #064e3b 0%, #022c22 100%);
        border: 2px dashed #10b981; border-radius: 15px;
        padding: 18px; margin-top: 20px; margin-bottom: 20px; text-align: center;
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.25);
    }
    
    /* Verification Box Styling Block Setup */
    .payment-form-box {
        background: linear-gradient(145deg, #0f172a 0%, #1e1b4b 100%);
        border: 3px solid #f59e0b; border-radius: 20px;
        padding: 22px; margin-top: 15px; margin-bottom: 25px;
        box-shadow: 0 0 25px rgba(245, 158, 11, 0.25);
    }
    
    /* Global Tactical Custom Action Buttons Layout */
    .stButton>button {
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 900 !important; font-size: 15px !important;
        border-radius: 12px !important; padding: 10px 0 !important;
        background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%) !important;
        color: #000000 !important; border: none !important;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4) !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.6) !important;
    }
    
    /* Custom Styled Interactive Google Auth Accent Single Sign-On Asset */
    .google-btn-mock {
        background-color: #ffffff !important; color: #1f2937 !important;
        border: 1px solid #e5e7eb !important; border-radius: 12px !important;
        font-size: 14px !important; padding: 12px !important; text-align: center;
        cursor: pointer; font-weight: 700; margin-bottom: 15px;
        display: flex; align-items: center; justify-content: center; gap: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15);
    }
    </style>
    """, unsafe_allow_html=True)

# Investment Nodes Pricing & Architecture Configuration 
LEVELS_CONF = {
    "VIP LEVEL 1": {"cost": 50, "daily_reward": 15},
    "VIP LEVEL 2": {"cost": 200, "daily_reward": 60},
    "VIP LEVEL 3": {"cost": 500, "daily_reward": 180}
}

# Realtime Execution Memory Storage Handlers
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "salmanveerm@gmail.com": {"balance": 5.00, "active_level": "None", "referred_by": "ubaid_rajput"},
        "ubaid_rajput": {"balance": 50.00, "active_level": "None", "referred_by": ""},
    }
if 'deposit_requests' not in st.session_state:
    st.session_state.deposit_requests = []

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'selected_payment_level' not in st.session_state: st.session_state.selected_payment_level = None

st.markdown('<div class="app-title-bar">📈 GLOBAL MATRIX INVESTMENT</div>', unsafe_allow_html=True)

# --- PORTAL REGISTRATION & GOOGLE AUTHENTICATION SECURITY GATEWAY ---
if not st.session_state.logged_in:
    st.markdown("<h4 style='text-align:center; color:#fff;'>SECURE PORTAL ACCOUNT HUB</h4>", unsafe_allow_html=True)
    
    # Custom Single Sign-On Premium Simulation Hook Element
    st.markdown("""
    <div class="google-btn-mock">
        <img src="https://fonts.gstatic.com/s/i/productlogos/googleg/v6/web-24dp/logo_googleg_color_24dp.png" width="18px"/>
        CONTINUE WITH GOOGLE / GMAIL CLIENT
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("📱 EMAIL REGISTERED ID / PHONE LINKAGE:", value="salmanveerm@gmail.com")
        password = st.text_input("🔒 SECURE NETWORK KEYCODE ENTRY:", type="password", placeholder="••••••••")
        
        if st.form_submit_button("🚀 UNLOCK PROTOCOL ARCHITECTURE", use_container_width=True):
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

# --- ADMIN DEPOSIT ACCOUNT VERIFICATION OPERATIONS PANEL ---
elif st.session_state.is_admin:
    st.markdown("<h3 style='color:#f59e0b; text-align:center;'>👑 CONTROL BACKEND CLEARING MATRIX</h3>", unsafe_allow_html=True)
    
    st.markdown('<div class="section-label">📥 TRANSACTION PROOF VALIDATION SLIPS</div>', unsafe_allow_html=True)
    if not st.session_state.deposit_requests:
        st.info("No system verification files pending ledger update action.")
    else:
        for idx, req in enumerate(st.session_state.deposit_requests):
            with st.container():
                st.markdown(f"""
                <div class='level-container' style='border-color: #f59e0b;'>
                    <span style='color:#f59e0b;'>NODE ID:</span> {req['user']}<br>
                    <span style='color:#f59e0b;'>VIP DEPLOY TARGET:</span> {req['level']}<br>
                    <span style='color:#f59e0b;'>TRANSACTION VALUE:</span> <b>RM {req['amount']}</b><br>
                    <span style='color:#f59e0b;'>HOLDER NAME:</span> {req['holder_name']}<br>
                    <span style='color:#f59e0b;'>REFERENCE HASH (TRX ID):</span> <code style='color:#10b981;'>{req['trx_id']}</code>
                </div>
                """, unsafe_allow_html=True)
                
                col_app, col_rej = st.columns(2)
                with col_app:
                    if st.button("✅ APPROVE DEPOSIT & FORCE SYNC", key=f"app_{idx}", use_container_width=True):
                        st.session_state.users_db[req['user']]["active_level"] = req['level']
                        
                        inviter = st.session_state.users_db[req['user']]["referred_by"]
                        if inviter in st.session_state.users_db:
                            if req['amount'] == 200:
                                st.session_state.users_db[inviter]["balance"] += 100.00
                            elif req['amount'] == 50:
                                st.session_state.users_db[inviter]["balance"] += 50.00
                        
                        st.session_state.deposit_requests.pop(idx)
                        st.success("Target ledger updated successfully!")
                        time.sleep(1)
                        st.rerun()
                with col_rej:
                    if st.button("❌ DECLINE FILE", key=f"rej_{idx}", use_container_width=True):
                        st.session_state.deposit_requests.pop(idx)
                        st.warning("Proof cancelled from pending queue stack.")
                        time.sleep(1)
                        st.rerun()

    st.markdown('<div class="section-label">⚙ CORE ADMINISTRATIVE DIRECT BALANCES SETTING</div>', unsafe_allow_html=True)
    target_user = st.selectbox("CHOOSE SYSTEM PROFILE TARGET:", list(st.session_state.users_db.keys()))
    new_bal = st.number_input("MANUAL ACCOUNT LIQUIDITY VALUE (RM):", min_value=0.0, value=float(st.session_state.users_db[target_user]["balance"]))
    set_lvl = st.selectbox("FORCE VIP PRIVILEGE LEVEL INDEX:", ["None", "VIP LEVEL 1", "VIP LEVEL 2", "VIP LEVEL 3"], index=["None", "VIP LEVEL 1", "VIP LEVEL 2", "VIP LEVEL 3"].index(st.session_state.users_db[target_user]["active_level"]))
    
    if st.button("💾 OVERRIDE PROFILE ACCOUNT LEDGER STATUS", use_container_width=True):
        st.session_state.users_db[target_user]["balance"] = new_bal
        st.session_state.users_db[target_user]["active_level"] = set_lvl
        st.success(f"LEDGER SYNC COMPLETED: Data parameters updated.")
        time.sleep(1)
        st.rerun()

    if st.button("🚪 LOGOUT ADMIN ROOT HUB TERMINAL", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()

# --- REVENUE DYNAMICS & ACCOUNT LIQUIDITY MATRIX PORTAL ---
else:
    current_user = st.session_state.current_user
    user_data = st.session_state.users_db[current_user]
    
    st.markdown(f"""
    <div class="balance-box">
        <div style="color:#8b949e; font-size:12px; letter-spacing:1px; margin-bottom:5px;">USER CLUSTER NODE ID: {current_user}</div>
        <div style="color:#e2e8f0; font-size:14px; letter-spacing:0.5px;">ACTIVE VIP TEIR: <span style="color:#f59e0b;">{user_data['active_level'].upper()}</span></div>
        <div style="color:#e2e8f0; font-size:15px; letter-spacing:0.5px; margin-top:5px;">TOTAL AVAILABLE WALLET LIQUIDITY</div>
        <div style="font-size:36px; color:#ffffff; margin-top:5px; text-shadow: 0 0 8px rgba(255,255,255,0.2);">RM {user_data['balance']:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

    col_dep, col_wdr = st.columns(2)
    with col_dep:
        if st.button("📥 DEPOSIT SLIP", use_container_width=True):
            st.info("Scroll down and select an un-purchased investment module node below to dynamically trigger verification panel.")
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
                st.success(f"🚀 SUCCESS: RM {w_amt} outward extraction transaction sent to checking vault.")
                time.sleep(1)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # --- NATIVE RENDERING GATEWAY MECHANISM (SCANNER DISPLAY FIX) ---
    if st.session_state.selected_payment_level:
        lvl_name = st.session_state.selected_payment_level
        lvl_cost = LEVELS_CONF[lvl_name]["cost"]
        
        st.markdown('<div class="payment-form-box">', unsafe_allow_html=True)
        st.markdown(f"<h3 style='margin:0; color:#ffffff; text-align:center;'>📥 SECURITY INBOUND VERIFICATION DETECTED</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#94a3b8; text-align:center; font-size:14px; margin-bottom:15px;'>TRANSFER CONTRACT SETUP AMOUNT: <b style='color:#f59e0b; font-size:20px;'>RM {lvl_cost}</b></p>", unsafe_allow_html=True)
        
        st.markdown("<p style='font-size:13px; color:#ffffff; font-weight:900;'>👇 SCAN OFFICIAL GATEWAY QR CODE DIRECTLY VIA YOUR APP:</p>", unsafe_allow_html=True)
        
        # SCAN RESOLUTION CRITICAL STABLE HOOK: Direct static fetch bypassing iframe connection refused constraints
        st.image("https://kommodo.ai/i/pt49bwYh6iJZi2gWV2EE", caption="SECURE FINANCIAL GATEWAY PROTOCOLS ONLY", use_container_width=True)
        
        # User input fields with explicit highly viewable labels styling tags
        holder_name = st.text_input("👤 SENDER ACCOUNT HOLDER NAME:", placeholder="Enter full sender legal account profile name")
        trx_id = st.text_input("🔢 TRANSACTION ID (TRX ID REFERENCE HASH):", placeholder="Enter unique banking slip 12-digit reference hex code")
        
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
                    st.success("✅ TRANSMITTED: Slip successfully sent to network clearance desk.")
                    st.session_state.selected_payment_level = None
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("❌ Execution error: Input boxes cannot remain blank!")
        with col_can_pay:
            if st.button("❌ ABORT VERIFICATION", use_container_width=True):
                st.session_state.selected_payment_level = None
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)

    # --- VIP PROCUREMENT NODES MODULE ---
    st.markdown('<div class="section-label">💎 AVAILABLE INVESTMENT CONTRACT PACKAGES</div>', unsafe_allow_html=True)
    
    for l_name, l_details in LEVELS_CONF.items():
        is_already_active = (user_data["active_level"] == l_name)
        active_status_text = " [CONTRACT CURRENTLY ACTIVE]" if is_already_active else ""
        
        st.markdown(f"""
        <div class="level-container">
            <div style="font-size:16px; color:#ffffff; margin-bottom:4px;">{l_name} <span style='color:#10b981;'>{active_status_text}</span></div>
            <div style="color:#94a3b8; font-size:13px;">DAILY RETRO CONTRACT PAYOUT: <span style="color:#10b981;">RM {l_details['daily_reward']:.2f}</span></div>
            <div style="color:#94a3b8; font-size:13px;">REQUIRED ACTIVATION ALLOCATION: <span style="color:#f59e0b;">RM {l_details['cost']}</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        if is_already_active:
            st.button(f"✅ MODULE NODE {l_name} LOADED", key=f"btn_act_{l_name}", disabled=True, use_container_width=True)
        else:
            if st.button(f"⚡ ALLOCATE CAPITAL TO {l_name}", key=f"btn_unl_{l_name}", use_container_width=True):
                if user_data["balance"] >= l_details['cost']:
                    st.session_state.users_db[current_user]["balance"] -= l_details['cost']
                    st.session_state.users_db[current_user]["active_level"] = l_name
                    st.success(f"🎉 COMPLETED: Activated contract sequence node {l_name} directly via internal assets wallet!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.session_state.selected_payment_level = l_name
                    st.warning(f"Allocation balance deficient! Complete secure inbound deposit form above.")
                    st.scroll_to_top()
                    st.rerun()

    # --- DYNAMIC PREMIUM CONTEXT-DRIVEN REFERRAL GENERATION HUB ---
    st.markdown(f"""
    <div class="invite-earn-box">
        <div style="font-size:18px; color:#10b981; margin-bottom:5px;">🤝 UNLIMITED REFERRAL DEPLOYER ACTIVE</div>
        <div style="font-size:14px; color:#ffffff; margin-bottom:10px;">INVITE FRIENDS TO ACCUMULATE INSANE EXTRA CAPITAL REWARDS</div>
        <div style="font-size:24px; color:#ffffff;">EARN UP TO <span style="color:#10b981;">RM 100.00</span> PER VALID NODE JOINED</div>
        <div style="background-color:rgba(0,0,0,0.4); border:1px solid #10b981; border-radius:8px; padding:8px; font-size:12px; color:#a7f3d0; margin-top:12px; font-family:monospace !important;">
            https://global-matrix-investment.streamlit.app/?ref={current_user.split('@')[0]}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- REALTIME TASK ENGINE WITH TIMEOUT DELAY MATRIX CONTROLS ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div style="border-top: 2px solid #1e293b; padding-top:12px;"></div>', unsafe_allow_html=True)

    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        if st.button("🏠 SYSTEM HOME", key="b_nav_h", use_container_width=True):
            st.session_state.selected_payment_level = None
            st.rerun()
            
    with col_b2:
        current_tier = user_data["active_level"]
        task_payout = 5.00 if current_tier == "None" else float(LEVELS_CONF[current_tier]["daily_reward"])
        
        if st.button(f"📊 WATCH AD/TASK (+{int(task_payout)})", key="b_nav_t", use_container_width=True):
            # REALTIME FIXED DELAY PIPELINE: Fake dynamic loop blockage prevention mechanism
            with st.spinner("⏳ LOADING SPONSOR MEDIA HIGH-REVENUE STREAM ADVERT... PLEASE DO NOT CLOSE PORTAL"):
                time.sleep(4.5)  # Forces 4.5 seconds real system block delay simulating heavy video render ad loading
            st.session_state.users_db[current_user]["balance"] += task_payout
            st.toast(f"🔒 TRANSACTION ROUTE SECURED: +RM {task_payout:.2f} credited!", icon="💰")
            time.sleep(1)
            st.rerun()
            
    with col_b3:
        if st.button("🚪 LOGOUT PROTOCOL", key="b_nav_l", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = ""
            st.session_state.selected_payment_level = None
            st.rerun()
