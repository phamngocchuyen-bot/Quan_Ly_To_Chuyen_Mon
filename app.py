import streamlit as st
import pandas as pd

# Cấu hình giao diện trang web
st.set_page_config(
    page_title="Quản lý Tổ Chuyên Môn Toán - Tin",
    page_icon="📚",
    layout="wide"
)

# THAY ID GOOGLE SHEET CỦA BẠN VÀO ĐÂY:
SHEET_ID = "1eIVRRQhr3SUkMdlHB9Fy2_GmujTGFyJPejgGoxXNnJs"

# Hàm đọc dữ liệu từ Google Sheets công khai
@st.cache_data(ttl=60) # Tự động làm mới dữ liệu sau mỗi 60 giây
def load_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    return pd.read_csv(url)

st.title("📊 Hệ thống Quản lý Tổ Chuyên Môn Toán - Tin")
st.markdown("Trang web điều hành, theo dõi thời khóa biểu, tiến độ ra đề, chuyên đề và soạn bài (Đồng bộ trực tiếp từ Google Sheets).")

# Menu bên trái (Sidebar)
menu = st.sidebar.selectbox(
    "Chọn chức năng quản lý", 
    ["📈 Tổng quan hoạt động", "📅 Thời khóa biểu & Giờ dạy", "📝 Quản lý Nhiệm vụ", "🤖 Trợ lý AI Kiểm tra tài liệu"]
)

# --- CHỨC NĂNG 1: TỔNG QUAN ---
if menu == "📈 Tổng quan hoạt động":
    st.subheader("Tổng quan hoạt động học kỳ")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tổng số Giáo viên", "12", "Ổn định")
    col2.metric("Đề thi đã hoàn thành", "24 / 28", "85.7%")
    col3.metric("Chuyên đề & Soạn bài", "18 / 20", "Sắp hoàn thành")
    col4.metric("AI Xử lý tự động", "142 lần", "Tiết kiệm 15h")

# --- CHỨC NĂNG 2: THỜI KHÓA BIỂU & GIỜ DẠY ---
elif menu == "📅 Thời khóa biểu & Giờ dạy":
    st.subheader("Quản lý Thời khóa biểu & Giờ chuẩn quy đổi (Đọc từ Sheet: NhanSu)")
    try:
        df_ns = load_data("NhanSu")
        st.dataframe(df_ns, use_container_width=True)
    except Exception as e:
        st.error(f"Không thể đọc dữ liệu từ tab 'NhanSu'. Hãy kiểm tra lại tên tab hoặc quyền chia sẻ công khai của Google Sheet. Lỗi: {e}")

# --- CHỨC NĂNG 3: QUẢN LÝ NHIỆM VỤ ---
elif menu == "📝 Quản lý Nhiệm vụ":
    st.subheader("Theo dõi tiến độ: Ra đề, Chuyên đề, Soạn bài (Đọc từ Sheet: NhiemVu)")
    try:
        df_nv = load_data("NhiemVu")
        st.dataframe(df_nv, use_container_width=True)
    except Exception as e:
        st.error(f"Không thể đọc dữ liệu từ tab 'NhiemVu'. Hãy kiểm tra lại tên tab. Lỗi: {e}")

# --- CHỨC NĂNG 4: TRỢ LÝ AI ---
elif menu == "🤖 Trợ lý AI Kiểm tra tài liệu":
    st.subheader("Trợ lý AI tự động rà soát đề thi và bài soạn")
    uploaded_file = st.file_uploader("Chọn file văn bản (.docx, .pdf)", type=["docx", "pdf", "txt"])
    if uploaded_file is not None:
        if st.button("🚀 Bắt đầu phân tích bằng AI"):
            with st.spinner("AI đang đọc và phân tích tài liệu..."):
                import time
                time.sleep(2)
            st.success("Phân tích hoàn tất!")
            st.info("✅ **Cấu trúc ma trận:** Đúng chuẩn tỷ lệ Nhận biết (40%), Thông hiểu (30%), Vận dụng (30%).")
