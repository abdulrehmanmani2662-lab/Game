import streamlit as st
import pandas as pd
import random
import time
import requests

# Page Setup
st.set_page_config(page_title="Global Matrix Investment", page_icon="📈", layout="centered")

# Google Sheet Web App URL (Aapka Google Script Link yahan aayega)
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbw-qngxwhZhlH07e6-wROfPnOd9jLGBfavoBoVcCfPqgk_AxiUnQTLOsr3CbLficPIMwQ/exec"

# --- PREMIUM DARK THEME CSS ---
st.markdown("""
    <style>
    header, footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"] { 
        display: none !important; visibility: hidden !important;
    }
    body { background-color: #121212; color: white; }
    .main .block-container { padding-top: 10px !important; padding-bottom:60px !important; }
    
    .gmig-header {
        background: #1a1a1a; padding: 20px; border-radius: 0 0 20px 20px;
        text-align: center; border-bottom: 2px solid #b8860b; margin-bottom: 20px;
    }
    .balance-card {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        padding: 20px; border-radius: 15px; border: 1px solid #374151;
        margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .method-box {
        background: #1e293b; padding: 15px; border-radius: 10px;
        border: 1px solid #475569; margin-bottom: 15px;
    }
    .qr-container {
        text-align: center;
        background: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Session States
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_tab' not in st.session_state: st.session_state.current_tab = "Home"
if 'sub_page' not in st.session_state: st.session_state.sub_page = "Main"
if 'user_wallet' not in st.session_state: st.session_state.user_wallet = 0.00
if 'user_phone' not in st.session_state: st.session_state.user_phone = "011-XXXXXXX"

# --- LOGIN ---
if not st.session_state.logged_in:
    st.markdown('<div class="gmig-header"><div style="font-size:24px; font-weight:bold; color:#e0533c;">Global Matrix Investment</div><div style="color:#aaa; font-size:12px;">Malaysia VIP Portal</div></div>', unsafe_allow_html=True)
    with st.form("gmig_login"):
        email = st.text_input("📧 E-mail / Phone Number", placeholder="Enter your registered account")
        pwd = st.text_input("🔒 Password", type="password", placeholder="Enter password")
        if st.form_submit_button("Sign In", use_container_width=True):
            if email and pwd:
                st.session_state.logged_in = True
                st.session_state.user_phone = email
                st.rerun()
else:
    # ----------------- 🏠 HOME TAB -----------------
    if st.session_state.current_tab == "Home":
        
        # RECHARGE PAGE
        if st.session_state.sub_page == "Recharge":
            st.markdown("### 📥 Deposit / Recharge Account")
            if st.button("⬅️ Back to Dashboard"):
                st.session_state.sub_page = "Main"
                st.rerun()
                
            dep_method = st.selectbox("Select Deposit Method:", ["Touch 'n Go (TNG eWallet)", "Local Bank Transfer", "Cryptocurrency (USDT-TRC20)"])
            
            if dep_method == "Touch 'n Go (TNG eWallet)":
                st.markdown("""
                <div class="method-box">
                    <h4 style="color:#3b82f6; margin:0 0 10px 0;">📱 Touch 'n Go Payment</h4>
                    <p><b>Step 1:</b> Scan this official QR code to make your deposit:</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Image embedded directly using your link
                st.image("https://kommodo.ai/i/pt49bwYh6iJZi2gWV2EE", caption="Mani Rajput Official TNG Scanner", width=300)
                
                st.markdown("""
                <div class="method-box">
                    <p><b>Step 2:</b> After successful transfer, enter your Ref No. and amount below.</p>
                </div>
                """, unsafe_allow_html=True)
                
            elif dep_method == "Local Bank Transfer":
                st.markdown("""
                <div class="method-box">
                    <h4 style="color:#f59e0b; margin:0 0 10px 0;">🏦 Malaysia Bank Details</h4>
                    <p><b>Bank Name:</b> Maybank / CIMB (Aap apna bank daalhein)</p>
                    <p><b>Account Number:</b> 1234-5678-9012</p>
                    <p><b>Account Title:</b> MANI RAJPUT</p>
                </div>
                """, unsafe_allow_html=True)
                
            elif dep_method == "Cryptocurrency (USDT-TRC20)":
                st.markdown("""
                <div class="method-box">
                    <h4 style="color:#10b981; margin:0 0 10px 0;">🟢 USDT TRC20 Address</h4>
                    <p><b>Network:</b> TRC20 (Tron)</p>
                    <code>TY76xXyZ...Aap_Ka_Crypto_Address...789</code>
                    <p style="font-size:12px; color:#ef4444; margin-top:5px;">*Send only USDT TRC20 tokens, otherwise funds will be lost.</p>
                </div>
                """, unsafe_allow_html=True)
                
            with st.form("deposit_submit"):
                amount = st.number_input("Enter Amount Deposited (RM or USDT):", min_value=10, value=50)
                ref_id = st.text_input("Transaction Reference ID / Ref No:", placeholder="e.g. TNG123456789")
                if st.form_submit_button("🔥 SUBMIT DEPOSIT PROOF"):
                    if ref_id:
                        try: requests.post(WEB_APP_URL, json={"action": "deposit", "phone": st.session_state.user_phone, "method": dep_method, "amount": amount, "ref": ref_id})
                        except: pass
                        st.success("🎉 Deposit submitted! Admin will verify and update your balance in 10-15 minutes.")
                    else: st.error("Please enter Reference ID!")

        # WITHDRAW PAGE
        elif st.session_state.sub_page == "Withdraw":
            st.markdown("### 📤 Withdraw Funds")
            if st.button("⬅️ Back to Dashboard"):
                st.session_state.sub_page = "Main"
                st.rerun()
                
            with st.form("withdraw_submit"):
                w_method = st.selectbox("Withdraw To:", ["Touch 'n Go", "Local Bank Transfer", "Crypto (USDT)"])
                w_acc = st.text_input("Enter Account Number / Phone / Wallet Address:")
                w_title = st.text_input("Account Holder Name (Title):")
                w_amount = st.number_input("Amount to Withdraw (Min RM 50):", min_value=50, value=50)
                
                if st.form_submit_button("💸 REQUEST WITHDRAWAL"):
                    if w_acc and w_title:
                        try: requests.post(WEB_APP_URL, json={"action": "withdraw", "phone": st.session_state.user_phone, "method": w_method, "account": w_acc, "title": w_title, "amount": w_amount})
                        except: pass
                        st.success("🚀 Withdrawal request sent successfully! Checking in progress.")
                    else: st.error("Please fill all details.")

        # MAIN HOME DASHBOARD VIEW
        else:
            st.markdown(f"""
            <div class="balance-card">
                <span style="color:#9ca3af; font-size:13px;">Account: {st.session_state.user_phone}</span><br>
                <span style="color:#9ca3af; font-size:14px;">Total Balance</span><br>
                <span style="font-size:32px; font-weight:bold; color:#fff;">RM {st.session_state.user_wallet:.2f}</span>
            </div>
            """, unsafe_allow_html=True)
            
            col_dep, col_wit = st.columns(2)
            with col_dep:
                if st.button("📥 RECHARGE", use_container_width=True):
                    st.session_state.sub_page = "Recharge"
                    st.rerun()
            with col_wit:
                if st.button("📤 WITHDRAW", use_container_width=True):
                    st.session_state.sub_page = "Withdraw"
                    st.rerun()
                    
            st.markdown("### 📺 YouTube Video Tasks")
            st.info("Watch videos below to claim your daily rewards.")
            if st.button("✅ CLAIM VIDEO WATCH REWARD (RM 5.00)", use_container_width=True):
                st.session_state.user_wallet += 5.00
                st.success("RM 5.00 added!")
                time.sleep(1)
                st.rerun()

    # --- PROJECTS TAB ---
    elif st.session_state.current_tab == "Project":
        st.markdown("### 💎 Investment Project Hall")
        st.write("Choose VIP levels to unlock higher daily profit limits.")

    # --- NAVIGATION ACTIONS ---
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏠 Home"): 
            st.session_state.current_tab = "Home"
            st.session_state.sub_page = "Main"
            st.rerun()
    with c2:
        if st.button("📊 Project"): st.session_state.current_tab = "Project"; st.rerun()
    with c3:
        if st.button("🚪 Logout"): st.session_state.logged_in = False; st.rerun()
