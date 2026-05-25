import streamlit as st
import pandas as pd
import requests
import random
import time
import smtplib
from email.mime.text import MIMEText

# Page Config
st.set_page_config(page_title="Mani Rewards Portal", page_icon="💰", layout="centered")

# --- CUSTOM CSS: PRO VIP SYSTEM ---
st.markdown("""
    <style>
    header, footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"] { 
        display: none !important; visibility: hidden !important;
    }
    .main .block-container { padding-top: 10px !important; padding-bottom:60px !important; }
    
    .gold-box {
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 50%, #000000 100%);
        padding: 20px; border-radius: 15px; text-align: center;
        color: #FFD700; border: 2px solid #FFD700; margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .ticker-wrap {
        background: #fff3cd; padding: 8px; border-radius: 8px;
        color: #856404; font-weight: bold; text-align: center; margin-bottom: 15px;
        border: 1px solid #ffeeba; font-size: 14px;
    }
    .task-card {
        background: white; padding: 20px; border-radius: 12px;
        border-left: 8px solid #FFD700; margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); color: black;
    }
    .vip-btn {
        background: linear-gradient(135deg, #FFD700 0%, #b8860b 100%);
        color: black !important; font-weight: bold; text-align: center;
        padding: 10px; border-radius: 8px; display: block; text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GOOGLE SHEET WEB APP URL ---
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbw-qngxwhZhlH07e6-wROfPnOd9jLGBfavoBoVcCfPqgk_AxiUnQTLOsr3CbLficPIMwQ/exec"

# --- REAL EMAIL OTP CONFIG (Mani Bhai Ki Asli Gmail Details) ---
ADMIN_GMAIL = "apnireal12@gmail.com"
ADMIN_APP_PASSWORD = "HkFeHJSRWxqt_2"

def send_real_otp(receiver_email, otp_code):
    msg = MIMEText(f"💰 Salam!\n\nMani Rewards Portal par account active karne ke liye aapka verification code yeh hai:\n\n🔥 CODE: {otp_code}\n\nYeh code kisi ke sath share na karein.\n\nRegards,\nMani Rajput Network Ltd.")
    msg['Subject'] = '🔒 Account OTP Code - Mani Rewards'
    msg['From'] = ADMIN_GMAIL
    msg['To'] = receiver_email
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(ADMIN_GMAIL, ADMIN_APP_PASSWORD)
            server.sendmail(ADMIN_GMAIL, receiver_email, msg.as_string())
        return True
    except Exception as e:
        return False

# Session States Manager
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_data' not in st.session_state: st.session_state.user_data = None
if 'view' not in st.session_state: st.session_state.view = "Login"
if 'generated_otp' not in st.session_state: st.session_state.generated_otp = None
if 'temp_reg_data' not in st.session_state: st.session_state.temp_reg_data = None

# VIP Header
st.markdown("""
    <div class="gold-box">
        <span style="font-size: 11px; text-transform: uppercase; letter-spacing: 2px; color: #fff;">Mani Rajput Network Ltd</span><br>
        <span style="font-size: 26px; font-weight: 900; font-family: 'Arial Black', sans-serif;">💰 MANI REWARDS</span><br>
        <span style="font-size: 13px; color: #FFD700;">Promote Blood Welfare & Earn Daily Cash</span>
    </div>
    """, unsafe_allow_html=True)

# Live Ticker
names_pool = ["Faisal", "Billa", "Ubaid Rajput", "Zeeshan", "Ali", "Zahid"]
cities_pool = ["Pindi Amolak", "Zafrwal", "Sialkot", "Narowal"]
st.markdown(f"""
    <div class="ticker-wrap">
        🔥 Live Alert: {random.choice(names_pool)} ({random.choice(cities_pool)}) just withdrew Rs. 1,200 via EasyPaisa!
    </div>
    """, unsafe_allow_html=True)

# --- DASHBOARD (LOGGED IN VIEW) ---
if st.session_state.logged_in:
    u = st.session_state.user_data
    
    st.markdown(f"""
    <div style="background:#111; padding:20px; border-radius:12px; border:2px solid #FFD700; color:white; margin-bottom:20px;">
        <span style="color:#aaa; font-weight:bold; font-size:12px;">📊 USER DASHBOARD</span><br>
        <span style="font-size:20px; font-weight:bold;">Slam, {u['name']}!</span><br><br>
        <span style="color:#FFD700; font-size:14px;">💵 CURRENT WALLET BALANCE</span><br>
        <span style="font-size:36px; font-weight:900; color:#fff;">Rs. {u['balance']}</span><br>
        <div style="margin-top:10px; font-size:14px;">🏅 Level status: <b style="color:#FFD700;">{u['level']}</b></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 Your Daily Tasks")
    st.write("Neeche diye gaye task ko poora karein aur har kamyab entry par Rs. 10 kamaein:")
    
    st.markdown(f"""
    <div class="task-card">
        <h4>Task 1: Blood Portal Par Naya Donor Join Karwayen</h4>
        <p>Hamari official Blood Website kholein, kisi bhi dost ya ilaqe ke bande ka real data register karein. Register karne ke baad uska naam niche proof mein likhein.</p>
        <a href="https://punjab-blood.streamlit.app/" target="_blank" class="vip-btn">🔗 OPEN BLOOD PORTAL</a>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("task_submit_form"):
        proof_name = st.text_input("Enter Registered Donor Name (Proof):", placeholder="e.g. Faisal Rajput")
        if st.form_submit_button("SUBMIT PROOF"):
            if proof_name:
                st.success("🎯 Proof Submitted! Admin verify kar ke Rs. 10 aapke wallet mein add kar dega.")
            else:
                st.warning("Proof likhna laazmi hai.")
                
    st.markdown("### 👥 Invite & Earn (Rs. 100 Per Friend)")
    ref_link = f"https://mani-rewards.streamlit.app/?ref={u['phone']}"
    st.info(f"Apna referral link doston ko bhejein, jab wo 50/- deposit karenge toh aapko Rs. 100 direct milenge:\n`{ref_link}`")

    if st.button("🚪 Logout Account"):
        st.session_state.logged_in = False
        st.session_state.user_data = None
        st.rerun()

# --- LOGIN / REGISTRATION SYSTEM ---
else:
    q_params = st.query_params
    ref_code = q_params.get("ref", "None")

    tab1, tab2 = st.tabs(["🔐 ACCOUNT LOGIN", "📝 CREATE ACCOUNT"])
    
    with tab1:
        l_phone = st.text_input("Mobile Number")
        l_pwd = st.text_input("Password", type="password")
        if st.button("🚀 SIGN IN"):
            if l_phone and l_pwd:
                with st.spinner("Checking details..."):
                    try:
                        res = requests.post(WEB_APP_URL, json={"action": "login", "phone": l_phone, "password": l_pwd}).json()
                        if res["status"] == "success":
                            st.session_state.logged_in = True
                            st.session_state.user_data = res["user"]
                            st.rerun()
                        else:
                            st.error("Nambar ya Password ghalat hai!")
                    except:
                        st.session_state.logged_in = True
                        st.session_state.user_data = {"name": "Mani Rajput", "balance": "100", "level": "Sipahi", "phone": l_phone}
                        st.rerun()
            else:
                st.warning("Dono fields fill karein.")
                
    with tab2:
        if st.session_state.generated_otp is None:
            r_name = st.text_input("Full Name")
            r_email = st.text_input("Gmail Address")
            r_phone = st.text_input("Mobile Number (EasyPaisa/JazzCash)")
            r_pwd = st.text_input("Create Password", type="password")
            
            if ref_code != "None":
                st.success(f"🔗 Referral Code Detected: {ref_code}")
                
            if st.button("🔥 SEND VERIFICATION CODE"):
                if r_name and r_email and r_phone and r_pwd:
                    with st.spinner("Verifying duplicate accounts..."):
                        try:
                            check = requests.post(WEB_APP_URL, json={"action": "check_user", "phone": r_phone, "email": r_email}).json()
                            if check["status"] == "exists":
                                st.error("⚠️ Is Number ya Email par pehle hi account bana hua hai!")
                                st.stop()
                        except: pass
                        
                        otp = str(random.randint(1000, 9999))
                        st.session_state.generated_otp = otp
                        st.session_state.temp_reg_data = {
                            "name": r_name, "email": r_email, "phone": r_phone, "password": r_pwd, "referred_by": ref_code
                        }
                        
                        with st.spinner("Sending real verification code to email..."):
                            mail_sent = send_real_otp(r_email, otp)
                            if mail_sent:
                                st.success("📩 Code aapki Email par bhej diya gaya hai!")
                            else:
                                st.error("❌ Email bhejney me masla aya. Settings check krein.")
                        st.rerun()
                else:
                    st.warning("Saari fields fill karein.")
        else:
            st.info(f"Code aapki email ({st.session_state.temp_reg_data['email']}) par bhej diya gaya hai.")
            ent_otp = st.text_input("Enter 4-Digit Code:")
            if st.button("🎯 ACTIVE MY ACCOUNT"):
                if ent_otp == st.session_state.generated_otp:
                    with st.spinner("Creating profile & adding Rs. 100 starting bonus..."):
                        try:
                            requests.post(WEB_APP_URL, json={
                                "action": "register",
                                "name": st.session_state.temp_reg_data["name"],
                                "email": st.session_state.temp_reg_data["email"],
                                "phone": st.session_state.temp_reg_data["phone"],
                                "password": st.session_state.temp_reg_data["password"],
                                "referred_by": st.session_state.temp_reg_data["referred_by"]
                            })
                        except: pass
                        st.success("🎉 Account Verified & Active! Rs. 100 Sign-up Bonus Added.")
                        st.session_state.generated_otp = None
                        st.session_state.view = "Login"
                        time.sleep(2)
                        st.rerun()
                else:
                    st.error("Ghalat code!")
