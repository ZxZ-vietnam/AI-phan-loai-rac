import streamlit as st
import pandas as pd
import base64
import os
import random

# ==========================================
# 1. CẤU HÌNH & HÀM HỖ TRỢ (DI CHUYỂN LÊN ĐẦU)
# ==========================================
st.set_page_config(page_title="ECOSORT", page_icon="♻️", layout="wide")

def play_ting_sound():
    # Link TRỰC TIẾP đến file mp3
    sound_url = "https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"
    sound_html = f"""
        <div style="display:none">
            <iframe src="{sound_url}" allow="autoplay"></iframe>
            <audio autoplay><source src="{sound_url}" type="audio/mp3"></audio>
        </div>
    """
    st.components.v1.html(sound_html, height=0)

def get_base64_img(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

@st.cache_data
def load_data():
    if os.path.exists("data_rac.csv"): return pd.read_csv("data_rac.csv")
    return None

# ==========================================
# 2. GIAO DIỆN CSS (GIỮ NGUYÊN 100%)
# ==========================================
st.markdown("""
    <style>
    .main-title { text-align: center; font-size: 32px; font-weight: bold; margin-bottom: 25px; color: #4CAF50; }
    @keyframes pulsePop {
        0% { transform: scale(1); }
        30% { transform: scale(0.9); }
        100% { transform: scale(1.1); }
    }
    .bin-box { 
        text-align: center; padding: 20px; border-radius: 15px; 
        border: 1px solid #333; background-color: #161b22; 
        min-height: 250px; display: flex; flex-direction: column; align-items: center; justify-content: center;
        transition: all 0.3s ease;
    }
    .active-huuco { background-color: #1b4332 !important; border: 3px solid #4CAF50 !important; box-shadow: 0px 0px 20px #4CAF50; animation: pulsePop 0.4s ease-out forwards; }
    .active-taiche { background-color: #4d4610 !important; border: 3px solid #fbc02d !important; box-shadow: 0px 0px 20px #fbc02d; animation: pulsePop 0.4s ease-out forwards; }
    .active-hazar { background-color: #4d1010 !important; border: 3px solid #f44336 !important; box-shadow: 0px 0px 20px #f44336; animation: pulsePop 0.4s ease-out forwards; }
    .active-general { background-color: #102a4d !important; border: 3px solid #2196F3 !important; box-shadow: 0px 0px 20px #2196F3; animation: pulsePop 0.4s ease-out forwards; }
    .inactive { opacity: 0.15; filter: grayscale(100%); }
    .bin-img { max-width: 120px; max-height: 120px; object-fit: contain; }
    .bin-label { font-weight: bold; color: white; font-size: 17px; margin-top: 15px; }
    .ins-card { background-color: #262730; padding: 15px; border-left: 5px solid #4CAF50; border-radius: 5px; margin-bottom: 20px; line-height: 1.6; }
    .ins-title { color: #4CAF50; font-weight: bold; font-size: 18px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. KHỞI TẠO TRẠNG THÁI (SESSION STATE)
# ==========================================
df = load_data()

if 'show_ins' not in st.session_state: st.session_state['show_ins'] = True
if 'ket_qua_cu' not in st.session_state: st.session_state['ket_qua_cu'] = None
if 'random_idx' not in st.session_state: st.session_state['random_idx'] = 0
if 'play_sound' not in st.session_state: st.session_state['play_sound'] = False

# ==========================================
# 4. SIDEBAR & HƯỚNG DẪN
# ==========================================
with st.sidebar:
    if os.path.exists("vinschool_logo.png"):
        st.image("vinschool_logo.png", use_container_width=True)
    st.header("Tùy chỉnh rác")
    che_do = st.radio("Phương thức nhập dữ liệu:", ["Dữ liệu có sẵn (DB)", "Tự nhập thông số"])
    st.write("---")
    nguong_am = st.slider("Ngưỡng ẩm rác hữu cơ (%)", 0, 100, 50)
    if not st.session_state['show_ins']:
        if st.button("Hiện lại hướng dẫn"):
            st.session_state['show_ins'] = True
            st.rerun()

st.markdown('<div class="main-title">♻️ PHÂN LOẠI CÁC LOẠI RÁC KHÁC NHAU CÙNG ECOSORT ♻️</div>', unsafe_allow_html=True)

if st.session_state['show_ins']:
    c1, c2 = st.columns([0.94, 0.06])
    with c1:
        if che_do == "Dữ liệu có sẵn (DB)":
            st.markdown('<div class="ins-card"><div class="ins-title">HƯỚNG DẪN: DB</div>• Chọn mẫu hoặc Shuffle rồi nhấn Phân tích.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="ins-card"><div class="ins-title">HƯỚNG DẪN: TỰ NHẬP</div>• Chỉnh thông số rồi nhấn Phân tích.</div>', unsafe_allow_html=True)
    with c2:
        if st.button("❌", key="close_btn"):
            st.session_state['show_ins'] = False
            st.rerun()

# ==========================================
# 5. NHẬP LIỆU & NÚT SHUFFLE (FIX LỖI SHUFFLE)
# ==========================================
col_in, col_shuffle = st.columns([0.85, 0.15])
with col_in:
    if che_do == "Dữ liệu có sẵn (DB)" and df is not None:
        danh_sach = df['Tên rác'].unique()
        ten_rac = st.selectbox("Chọn mẫu rác:", danh_sach, index=st.session_state['random_idx'])
        dong = df[df['Tên rác'] == ten_rac].iloc[0]
        la_sinh_vat = bool(dong['Nguồn gốc sinh vật (1/0)'])
        do_am = float(str(dong['Độ ẩm (0-100)']).replace(',','.'))
    else:
        ten_rac = st.text_input("Tên mẫu vật:", "Mẫu mới")
        la_sinh_vat = st.toggle("Nguồn gốc sinh học")
        do_am = st.slider("Độ ẩm (%)", 0, 100, 25)

with col_shuffle:
    st.write(" ")
    st.write(" ")
    if st.button("🔀"):
        if df is not None and che_do == "Dữ liệu có sẵn (DB)":
            st.session_state['random_idx'] = random.randint(0, len(df['Tên rác'].unique()) - 1)
            st.session_state['ket_qua_cu'] = None  # Xóa kết quả cũ để không tự phân tích
            st.rerun()

la_nguy_hai = st.toggle("💉 Rác y tế / Nguy hại?")
nut_phan_tich = st.button("🔎 BẮT ĐẦU PHÂN TÍCH 🔍")

# ==========================================
# 6. LOGIC AI & BẬT CỜ ÂM THANH
# ==========================================
if nut_phan_tich:
    if la_nguy_hai: ket_qua = "nguyhai"
    elif la_sinh_vat and do_am >= nguong_am: ket_qua = "huuco"
    elif not la_sinh_vat and do_am < 40: ket_qua = "taiche"
    else: ket_qua = "voco"
    
    st.session_state['ket_qua_cu'] = ket_qua
    st.session_state['play_sound'] = True # Bật cờ âm thanh
    st.rerun()

# THỰC THI PHÁT ÂM THANH SAU KHI RERUN
if st.session_state.get('play_sound', False):
    play_ting_sound()
    if st.session_state['ket_qua_cu'] == "huuco": st.balloons()
    st.session_state['play_sound'] = False # Tắt cờ ngay để không bị lặp lại

hien_thi = st.session_state['ket_qua_cu']

# ==========================================
# 7. HIỂN THỊ KẾT QUẢ (GIỮ NGUYÊN GIAO DIỆN)
# ==========================================
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

# ==========================================
# 8. WOW FACTOR
# ==========================================
st.write("---")
with st.expander("🌍 Bạn có biết?"):
    facts = ["Một chai nhựa mất 450 năm để phân hủy.", "Rác hữu cơ làm phân bón rất tốt."]
    st.info(random.choice(facts))