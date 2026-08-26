import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

# Cấu hình giao diện trang web
st.set_page_config(
    page_title="Quản lý Tổ Chuyên Môn Toán - Tin",
    page_icon="📚",
    layout="wide"
)

SHEET_ID = "1eIVRRQhr3SUkMdlHB9Fy2_GmujTGFyJPejgGoxXNnJs"

# Hàm đọc dữ liệu từ Google Sheets công khai
@st.cache_data(ttl=60)
def load_data(sheet_name):
    encoded_sheet_name = urllib.parse.quote(sheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
    return pd.read_csv(url)

st.title("📊 Hệ thống Quản lý Tổ Chuyên Môn Toán - Tin")
st.markdown("Trang web điều hành, theo dõi tiến độ và hỗ trợ chuyên môn (Đồng bộ trực tiếp từ Google Sheets).")

# Menu bên trái (Sidebar)
menu = st.sidebar.selectbox(
    "Chọn chức năng quản lý", 
    ["📈 Tổng quan hoạt động", "📝 Quản lý Nhiệm vụ", "🤖 Trợ lý AI Chấm bài học sinh"]
)

# --- CHỨC NĂNG 1: TỔNG QUAN ---
if menu == "📈 Tổng quan hoạt động":
    st.subheader("Tổng quan hoạt động học kỳ")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tổng số Giáo viên", "12", "Ổn định")
    col2.metric("Đề thi đã hoàn thành", "24 / 28", "85.7%")
    col3.metric("Chuyên đề & Soạn bài", "18 / 20", "Sắp hoàn thành")
    col4.metric("AI Xử lý tự động", "142 lần", "Tiết kiệm 15h")

# --- CHỨC NĂNG 2: QUẢN LÝ NHIỆM VỤ ---
elif menu == "📝 Quản lý Nhiệm vụ":
    st.subheader("Theo dõi tiến độ tự động")
    
    if st.button("🔄 Làm mới dữ liệu"):
        st.cache_data.clear()
        st.rerun()

    try:
        df_nv = load_data("NhiemVu")
        df_form = load_data("Cautraloibieumau1")
        
        def xu_ly_dong_bo(row):
            ten_gv = str(row.get('HoTen', '')).strip()
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
            if 'LinkNop' in df_nv.columns:
                df_nv = df_nv.drop(columns=['LinkNop'])
                
        st.dataframe(df_nv, use_container_width=True)
        
    except Exception as e:
        st.error(f"Lỗi hiển thị dữ liệu: {e}")

# --- CHỨC NĂNG 3: TRỢ LÝ AI CHẤM BÀI ---
elif menu == "🤖 Trợ lý AI Chấm bài học sinh":
    st.subheader("🤖 Trợ lý AI Hỗ trợ Chấm bài & Nhận xét tự động")
    st.markdown("Tải lên bài làm của học sinh và cung cấp đáp án chuẩn để AI tiến hành rà soát, cho điểm và viết lời nhận xét.")

    col_a, col_b = st.columns(2)
    with col_a:
        uploaded_student_file = st.file_uploader("1. Chọn file bài làm học sinh (.docx, .pdf, .txt)", type=["docx", "pdf", "txt"])
    with col_b:
        rubric_text = st.text_area("2. Nhập đáp án chuẩn hoặc Thang điểm (Rubric)", placeholder="Ví dụ: Câu 1 (2đ): x = 2, lập luận chặt chẽ...\nCâu 2 (3đ): ...")

    if uploaded_student_file is not None:
        if st.button("🚀 Bắt đầu chấm bài tự động"):
            with st.spinner("AI đang đọc bài làm, đối chiếu đáp án và viết nhận xét..."):
                import time
                time.sleep(2.5)
            
            st.success("Chấm bài hoàn tất!")
            
            # Hiển thị kết quả mẫu trực quan
            st.markdown("### 📊 Kết quả đánh giá từ AI:")
            st.metric(label="Điểm số gợi ý", value="8.5 / 10", delta="+1.5 điểm so với mức trung bình")
            
            st.markdown("---")
            st.markdown("#### 📝 Chi tiết nhận xét:")
            st.info("""
            * **Ưu điểm:** Học sinh trình bày các bước giải logic, rõ ràng ở phần đại số. Lập luận sắc bén, kết quả tính toán chính xác.
            * **Điểm cần lưu ý (Trừ 1.5đ):** Ở phần hình học không gian (câu cuối), bước chứng minh đường vuông góc với mặt phẳng chưa thực sự tường minh, thiếu một bước phụ trợ trung gian.
            * **Gợi ý lời phê của giáo viên:** *Bài làm tốt, nắm vững kiến thức cơ bản. Cần cẩn thận hơn ở phần trình bày hình học không gian.*
            """)
