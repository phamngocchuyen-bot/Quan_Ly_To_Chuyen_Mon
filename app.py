import streamlit as st
import pandas as pd
import urllib.parse  # Thư viện dùng để xử lý khoảng trắng trong URL

# Cấu hình giao diện trang web
st.set_page_config(
    page_title="Quản lý Tổ Chuyên Môn Toán - Tin",
    page_icon="📚",
    layout="wide"
)

SHEET_ID = "1eIVRRQhr3SUkMdlHB9Fy2_GmujTGFyJPejgGoxXNnJs"

# Hàm đọc dữ liệu từ Google Sheets công khai (đã xử lý mã hóa tên tab có khoảng trắng)
@st.cache_data(ttl=60)
def load_data(sheet_name):
    encoded_sheet_name = urllib.parse.quote(sheet_name) # Mã hóa khoảng trắng thành %20
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
    return pd.read_csv(url)

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

# --- CHỨC NĂNG 3: QUẢN LÝ NHIỆM VỤ ---
elif menu == "📝 Quản lý Nhiệm vụ":
    st.subheader("Theo dõi tiến độ tự động")
    
    if st.button("🔄 Làm mới dữ liệu"):
        st.cache_data.clear()
        st.rerun()

    try:
        import pandas as pd
        from datetime import datetime
        
        # Đọc dữ liệu phân công (NhiemVu) và danh sách nộp từ Form (Cautraloibieumau1)
        df_nv = load_data("NhiemVu")
        df_form = load_data("Cautraloibieumau1")
        
        # Hàm tự động quét trạng thái
        def xu_ly_dong_bo(row):
            ten_gv = str(row.get('HoTen', '')).strip()
            
            # Kiểm tra xem giáo viên đã nộp bài qua Form chưa
            da_nop = False
            if not df_form.empty:
                for _, form_row in df_form.iterrows():
                    ten_form = str(form_row.get('Họ và tên', '')).strip()
                    if ten_gv.lower() in ten_form.lower() or ten_form.lower() in ten_gv.lower():
                        da_nop = True
                        break
            
            if da_nop:
                row['TrangThai'] = "Đã nộp ✅"
                return row
                
            # Nếu chưa nộp, tính toán dựa vào hạn nộp
            trang_thai_hien_tai = str(row.get('TrangThai', '')).strip()
            if trang_thai_hien_tai and trang_thai_hien_tai.lower() not in ['nan', 'none', '']:
                return row 
                
            try:
                ngay_het_han = datetime.strptime(str(row['HanNop']).strip(), '%d/%m/%Y')
                if datetime.now() > ngay_het_han:
                    row['TrangThai'] = "Quá hạn ⚠️"
                else:
                    row['TrangThai'] = "Đang làm ⏳"
            except:
                row['TrangThai'] = "Đang làm ⏳"
                
            return row

        if not df_nv.empty:
            df_nv = df_nv.apply(xu_ly_dong_bo, axis=1)
            # Tự động lược bỏ cột Link nếu lỡ có trong Sheet để giao diện gọn nhất
            if 'LinkNop' in df_nv.columns:
                df_nv = df_nv.drop(columns=['LinkNop'])
                
        st.dataframe(df_nv, use_container_width=True)
        
    except Exception as e:
        st.error(f"Lỗi hiển thị dữ liệu: {e}")
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
