import streamlit as st
import pandas as pd
import base64
import os

# 1. CẤU HÌNH TRANG & GIAO DIỆN (MÀU XANH ECO)
st.set_page_config(page_title="ECOSORT", page_icon="♻️", layout="wide")

# Màu xanh Eco: #4CAF50
st.markdown("""
    <style>
    .main-title { text-align: center; font-size: 32px; font-weight: bold; margin-bottom: 25px; color: #4CAF50; }
    .bin-box { 
        text-align: center; padding: 20px; border-radius: 15px; 
        border: 1px solid #333; background-color: #161b22; 
        min-height: 250px; display: flex; flex-direction: column; align-items: center; justify-content: center;
        transition: all 0.3s ease;
    }
    .active-huuco { background-color: #1b4332; border: 2px solid #4CAF50; box-shadow: 0px 0px 15px #4CAF50; }
    .active-taiche { background-color: #4d4610; border: 2px solid #fbc02d; box-shadow: 0px 0px 15px #fbc02d; }
    .active-hazar { background-color: #4d1010; border: 2px solid #f44336; box-shadow: 0px 0px 15px #f44336; }
    .active-general { background-color: #102a4d; border: 2px solid #2196F3; box-shadow: 0px 0px 15px #2196F3; }
    
    .inactive { opacity: 0.1; filter: grayscale(100%); }
    .bin-img { max-width: 120px; max-height: 120px; object-fit: contain; }
    .bin-label { font-weight: bold; color: white; font-size: 17px; margin-top: 15px; }
    
    /* Khung hướng dẫn viền xanh */
    .ins-card {
        background-color: #262730; padding: 15px; border-left: 5px solid #4CAF50;
        border-radius: 5px; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. HÀM HỖ TRỢ ĐỌC ẢNH
def get_base64_img(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

@st.cache_data
def load_data():
    if os.path.exists("data_rac.csv"): return pd.read_csv("data_rac.csv")
    return None

df = load_data()

# KHỞI TẠO BỘ NHỚ TẠM
if 'show_ins' not in st.session_state: st.session_state['show_ins'] = True
if 'ket_qua_cu' not in st.session_state: st.session_state['ket_qua_cu'] = None

# 3. THANH BÊN (SIDEBAR) - LOGO VINSCHOOL
with st.sidebar:
    if os.path.exists("vinschool_logo.png"):
        st.image("vinschool_logo.png", use_container_width=True)
    
    st.header("Tùy chỉnh rác")
    che_do = st.radio("Phương thức nhập dữ liệu:", ["Dữ liệu có sẵn (DB)", "Tự nhập thông số"])
    st.write("---")
    nguong_am = st.slider("Ngưỡng ẩm rác hữu cơ (%)", 0, 100, 50)
    
    if not st.session_state['show_ins']:
        st.write("---")
        if st.button("🔄 Hiện lại hướng dẫn"):
            st.session_state['show_ins'] = True
            st.rerun()

# 4. MÀN HÌNH CHÍNH
st.markdown('<div class="main-title">♻️ PHÂN LOẠI CÁC LOẠI RÁC KHÁC NHAU ♻️</div>', unsafe_allow_html=True)

# Hiển thị Hướng dẫn
if st.session_state['show_ins']:
    c1, c2 = st.columns([0.94, 0.06])
    with c1:
        st.markdown("""
        <div class="ins-card">
            <b>📖 HƯỚNG DẪN SỬ DỤNG:</b><br>
            1. Chọn mẫu vật tại Sidebar bên trái. | 2. Điều chỉnh ngưỡng ẩm AI phù hợp. | 3. Nhấn <b>Bắt đầu phân tích</b>.
        </div>
        """, unsafe_allow_html=True)
    with c2:
        if st.button("❌", key="close_btn"):
            st.session_state['show_ins'] = False
            st.rerun()

# 5. NHẬP LIỆU
col_in, _ = st.columns([1, 1])
with col_in:
    if che_do == "Dữ liệu có sẵn (DB)" and df is not None:
        ten_rac = st.selectbox("Chọn mẫu rác:", df['Tên rác'].unique())
        dong = df[df['Tên rác'] == ten_rac].iloc[0]
        la_sinh_vat = bool(dong['Nguồn gốc sinh vật (1/0)'])
        do_am = float(str(dong['Độ ẩm (0-100)']).replace(',','.'))
    else:
        ten_rac = st.text_input("Tên mẫu vật:", "Mẫu mới")
        la_sinh_vat = st.toggle("Nguồn gốc sinh học")
        do_am = st.slider("Độ ẩm (%)", 0, 100, 25)
    
    la_nguy_hai = st.toggle("💉 Rác y tế / Nguy hại?")
    nut_phan_tich = st.button("🔎 BẮT ĐẦU PHÂN TÍCH🔍")

# 6. LOGIC AI
if nut_phan_tich:
    if la_nguy_hai: ket_qua = "nguyhai"
    elif la_sinh_vat and do_am >= nguong_am: ket_qua = "huuco"
    elif not la_sinh_vat and do_am < 40: ket_qua = "taiche"
    else: ket_qua = "voco"
    
    if ket_qua == "huuco": st.balloons()
    st.session_state['ket_qua_cu'] = ket_qua

hien_thi = st.session_state['ket_qua_cu']

# 7. HIỂN THỊ KẾT QUẢ
st.write("---")
t1, t2, t3, t4 = st.columns(4)

anh_b64 = {
    "huuco": get_base64_img("huuco.png"),
    "taiche": get_base64_img("taiche.png"),
    "nguyhai": get_base64_img("voco.png"),
    "voco": get_base64_img("general.png")
}

thung_rac = [
    (t1, "huuco", "RÁC HỮU CƠ", "active-huuco"),
    (t2, "taiche", "RÁC TÁI CHẾ", "active-taiche"),
    (t3, "nguyhai", "RÁC NGUY HẠI", "active-hazar"),
    (t4, "voco", "VÔ CƠ KHÁC", "active-general")
]

for cot, ma, nhan, lop_css in thung_rac:
    with cot:
        style = lop_css if hien_thi == ma else "inactive"
        b64 = anh_b64.get(ma, "")
        st.markdown(f"""
            <div class="bin-box {style}">
                <img src="data:image/png;base64,{b64}" class="bin-img">
                <div class="bin-label">{nhan}</div>
            </div>
        """, unsafe_allow_html=True)