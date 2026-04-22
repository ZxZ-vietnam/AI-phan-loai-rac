import streamlit as st
import pandas as pd
import base64
import os
import random
import time

# 1. CẤU HÌNH TRANG
st.set_page_config(page_title="ECOSORT PRO", page_icon="♻️", layout="wide")

# 2. CSS NÂNG CAO - TRỰC DIỆN & DỨT KHOÁT
st.markdown("""
    <style>
    .main-title { text-align: center; font-size: 32px; font-weight: bold; color: #4CAF50; }
    
    /* Hiệu ứng Zoom Instant (Phóng to dứt khoát) */
    .bin-box { 
        text-align: center; padding: 20px; border-radius: 15px; 
        border: 1px solid #333; background-color: #161b22; 
        min-height: 250px; display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    
    /* Thùng rác được chọn sẽ to ra ngay lập tức */
    .active-bin { 
        transform: scale(1.1); 
        border: 4px solid #4CAF50 !important; 
        box-shadow: 0px 0px 20px #4CAF50;
        z-index: 99;
    }
    
    .inactive { opacity: 0.2; filter: grayscale(100%); }
    .bin-img { max-width: 120px; max-height: 120px; object-fit: contain; }

    /* Hiệu ứng Vứt rác Directly vào thùng */
    @keyframes tossIntoBin {
        0% { transform: translateY(-150px) scale(1.5); opacity: 1; }
        100% { transform: translateY(50px) scale(0); opacity: 0; }
    }
    .toss-animation {
        position: absolute; left: 0; right: 0; margin-left: auto; margin-right: auto;
        width: fit-content; z-index: 100;
        font-size: 30px; font-weight: bold; color: white;
        background: #4CAF50; padding: 10px 20px; border-radius: 50px;
        animation: tossIntoBin 0.6s ease-in forwards; /* Nhanh & dứt khoát */
    }
    
    /* Bọc hàng thùng rác để làm điểm tựa cho animation */
    .bin-container { position: relative; padding-top: 100px; }
    </style>
    """, unsafe_allow_html=True)

# 3. HÀM TRỢ GIÚP
def get_base64_img(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

@st.cache_data
def load_data():
    if os.path.exists("data_rac.csv"): return pd.read_csv("data_rac.csv")
    return None

df = load_data()

if 'selected_index' not in st.session_state: st.session_state.selected_index = 0
if 'show_anim' not in st.session_state: st.session_state.show_anim = False
if 'ket_qua_cu' not in st.session_state: st.session_state['ket_qua_cu'] = None

# 4. THANH BÊN
with st.sidebar:
    if os.path.exists("vinschool_logo.png"):
        st.image("vinschool_logo.png", use_container_width=True)
    nguong_am = st.slider("Ngưỡng ẩm hữu cơ (%)", 0, 100, 50)

# 5. MÀN HÌNH CHÍNH
st.markdown('<div class="main-title">♻️ ECO-SORT VINSCHOOL ♻️</div>', unsafe_allow_html=True)

# 6. NHẬP LIỆU & SHUFFLE
c1, c2 = st.columns([0.85, 0.15])
if df is not None:
    with c2:
        st.write(" ")
        if st.button("🔀"):
            st.session_state.selected_index = random.randint(0, len(df['Tên rác'].unique()) - 1)
            st.rerun()
    with c1:
        ten_rac = st.selectbox("Mẫu rác:", df['Tên rác'].unique(), index=st.session_state.selected_index)

    dong = df[df['Tên rác'] == ten_rac].iloc[0]
    la_sinh_vat = bool(dong['Nguồn gốc sinh vật (1/0)'])
    do_am = float(str(dong['Độ ẩm (0-100)']).replace(',','.'))
    
    if st.button("🎯 PHÂN TÍCH NGAY", use_container_width=True):
        if la_sinh_vat and do_am >= nguong_am: res = "huuco"
        elif not la_sinh_vat and do_am < 40: res = "taiche"
        else: res = "voco"
        st.session_state.ket_qua_cu = res
        st.session_state.show_anim = True

# 7. HIỂN THỊ KẾT QUẢ & ANIMATION
st.write("---")

# Container bọc 4 cột để làm điểm tựa cho rác bay
st.markdown('<div class="bin-container">', unsafe_allow_html=True)

# Nếu đang có animation, hiện cái rác bay đè lên hàng thùng
if st.session_state.show_anim:
    st.markdown(f'<div class="toss-animation">📦 {ten_rac}</div>', unsafe_allow_html=True)
    time.sleep(0.6) # Khớp với thời gian animation 0.6s
    st.session_state.show_anim = False
    st.rerun()

t1, t2, t3, t4 = st.columns(4)
hien_thi = st.session_state.ket_qua_cu

anh_b64 = {
    "huuco": get_base64_img("huuco.png"),
    "taiche": get_base64_img("taiche.png"),
    "nguyhai": get_base64_img("voco.png"),
    "voco": get_base64_img("general.png")
}

thung_rac = [
    (t1, "huuco", "HỮU CƠ", "active-huuco"),
    (t2, "taiche", "TÁI CHẾ", "active-taiche"),
    (t3, "nguyhai", "NGUY HẠI", "active-hazar"),
    (t4, "voco", "VÔ CƠ", "active-general")
]

for cot, ma, nhan, lop_css in thung_rac:
    with cot:
        is_active = (hien_thi == ma)
        lop_final = f"bin-box active-bin" if is_active else "bin-box inactive"
        b64 = anh_b64.get(ma, "")
        st.markdown(f"""
            <div class="{lop_final}">
                <img src="data:image/png;base64,{b64}" class="bin-img">
                <div style="color:white; font-weight:bold; margin-top:10px;">{nhan}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # Đóng bin-container