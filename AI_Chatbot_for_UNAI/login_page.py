import streamlit as st
from logic import supabase

def check_authentication():
    """Check if user is logged in"""
    if "user" not in st.session_state:
        st.session_state.user = None
    
    if st.session_state.user is None:
        show_login_page()
        st.stop()

def show_login_page():
    """Display login/signup page"""
    st.title("🤖 UNAI Chatbot")
    st.markdown("### ล็อกอินเพื่อใช้งาน")
    
    tab1, tab2 = st.tabs(["เข้าสู่ระบบ", "สมัครสมาชิก"])
    
    with tab1:
        st.subheader("เข้าสู่ระบบ")
        email = st.text_input("อีเมล", key="login_email", placeholder="your@email.com")
        password = st.text_input("รหัสผ่าน", type="password", key="login_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("เข้าสู่ระบบ", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("กรุณากรอกอีเมลและรหัสผ่าน")
                else:
                    try:
                        response = supabase.auth.sign_in_with_password({
                            "email": email,
                            "password": password
                        })
                        st.session_state.user = response.user
                        st.success("เข้าสู่ระบบสำเร็จ!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"เข้าสู่ระบบไม่สำเร็จ: {str(e)}")
    
    with tab2:
        st.subheader("สมัครสมาชิก")
        email = st.text_input("อีเมล", key="signup_email", placeholder="your@email.com")
        password = st.text_input("รหัสผ่าน", type="password", key="signup_password")
        confirm_password = st.text_input("ยืนยันรหัสผ่าน", type="password", key="confirm_password")
        
        if st.button("สมัครสมาชิก", use_container_width=True, type="primary"):
            if not email or not password:
                st.error("กรุณากรอกข้อมูลให้ครบถ้วน")
            elif password != confirm_password:
                st.error("รหัสผ่านไม่ตรงกัน")
            elif len(password) < 6:
                st.error("รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร")
            else:
                try:
                    response = supabase.auth.sign_up({
                        "email": email,
                        "password": password
                    })
                    st.success("สมัครสมาชิกสำเร็จ! กรุณาตรวจสอบอีเมลเพื่อยืนยันบัญชี")
                    st.info("กลับไปที่แท็บ 'เข้าสู่ระบบ' เพื่อเข้าใช้งาน")
                except Exception as e:
                    st.error(f"สมัครสมาชิกไม่สำเร็จ: {str(e)}")

def logout():
    """Logout user"""
    try:
        supabase.auth.sign_out()
        st.session_state.user = None
        st.session_state.chat_sessions = {}
        st.success("ออกจากระบบสำเร็จ")
        st.rerun()
    except Exception as e:
        st.error(f"ออกจากระบบไม่สำเร็จ: {str(e)}")
