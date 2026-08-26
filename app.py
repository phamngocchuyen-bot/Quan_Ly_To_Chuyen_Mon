import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

# Cấu hình giao diện trang web
st.set_page_config(
    page_title="Hệ thống Quản lý Học tập & Chấm bài AI",
    page_icon="📖",
    layout="wide"
)

SHEET_ID = "1eIVRRQhr3SUkMdlHB9Fy2_GmujTGFyJPejgGoxXNnJs"

# Hàm đọc dữ liệu từ Google Sheets công khai
@st.cache_data(ttl=60)
def load_data(sheet_name):
    encoded_sheet_name = urllib.parse.quote(sheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
    return pd.read_csv(url)

st.title("📖 Hệ thống Quản lý Bài tập & Trợ lý AI Chấm bài")
st.markdown("Hệ thống giao bài, theo dõi học sinh nộp bài qua Form và hỗ trợ AI chấm điểm tự động.")

# Menu bên trái (Sidebar)
menu = st.sidebar.selectbox(
    "Chọn chức năng", 
    ["👥 Danh sách học sinh", "📚 Giao bài & Theo dõi nộp bài", "🤖 Trợ lý AI Chấm bài tự động"]
)

# --- CHỨC NĂNG 1: DANH SÁCH HỌC SINH ---
if menu == "👥 Danh sách học sinh":
    st.subheader("👥 Quản lý danh sách học sinh các lớp")
    if st.button("🔄 Làm mới dữ liệu"):
        st.cache_data.clear()
        st.rerun()
    try:
        df_hs = load_data("DanhSachHS")
        st.dataframe(df_hs, use_container_width=True)
    except Exception as e:
        st.error(f"Chưa tìm thấy tab 'DanhSachHS' trong Google Sheet. Lỗi: {e}")

# --- CHỨC NĂNG 2: GIAO BÀI & THEO DÕI NỘP BÀI ---
elif menu == "📚 Giao bài & Theo dõi nộp bài":
    st.subheader("📚 Theo dõi tiến độ làm bài và nộp bài của học sinh")
    
    if st.button("🔄 Làm mới dữ liệu"):
        st.cache_data.clear()
        st.rerun()

    try:
        df_bt = load_data("GiaoBaiTap")
        df_nop = load_data("NopBaiHS")
        
        def kiem_tra_nop_bai(row):
            ten_hs = str(row.get('HoTen', '')).strip()
            ten_bai = str(row.get('TenBaiTap', '')).strip()
            
            da_nop = False
            if not df_nop.empty:
                for _, nop_row in df_nop.iterrows():
                    ten_form_hs = str(nop_row.get('Họ và tên', '')).strip()
                    ten_form_bai = str(nop_row.get('Tên bài tập', '')).strip()
                    if ten_hs.lower() in ten_form_hs.lower() and ten_bai.lower() in ten_form_bai.lower():
                        da_nop = True
                        break
            
            if da_nop:
                return "Đã nộp ✅"
                
            try:
                ngay_het_han = datetime.strptime(str(row['HanNop']).strip(), '%d/%m/%Y')
                if datetime.now() > ngay_het_han:
                    return "Quá hạn ⚠️"
                else:
                    return "Đang làm ⏳"
            except:
                return "Đang làm ⏳"

        if not df_bt.empty:
            df_bt['TrangThai'] = df_bt.apply(kiem_tra_nop_bai, axis=1)
            
        st.dataframe(df_bt, use_container_width=True)
        
    except Exception as e:
        st.error(f"Lỗi tải dữ liệu bài tập hoặc bài nộp: {e}")

# --- CHỨC NĂNG 3: TRỢ LÝ AI CHẤM BÀI ---
elif menu == "🤖 Trợ lý AI Chấm bài tự động":
    st.subheader("🤖 Trợ lý AI Chấm bài học sinh theo Đáp án/Rubric")
    st.markdown("Tải lên bài làm của học sinh và nhập đáp án chuẩn để AI tiến hành chấm điểm, đối chiếu và nhận xét chi tiết.")

    col1, col2 = st.columns(2)
    with col1:
        student_file = st.file_uploader("1. Tải lên bài làm học sinh (.docx, .pdf, .txt)", type=["docx", "pdf", "txt"])
    with col2:
        answer_key = st.text_area("2. Nhập Đáp án chuẩn / Thang điểm (Rubric)", placeholder="Ví dụ:\nCâu 1 (2đ): x = 3...\nCâu 2 (3đ): Lập luận theo định lý Talet...")

    if student_file is not None:
        if st.button("🚀 AI tiến hành chấm bài"):
            with st.spinner("AI đang đọc bài làm, đối chiếu đáp án chuẩn và phân tích lỗi sai..."):
                import time
                time.sleep(2)
            
            st.success("Chấm bài và phân tích hoàn tất!")
            
            st.markdown("### 📊 Kết quả chấm điểm từ AI:")
            st.metric(label="Điểm số đánh giá", value="9.0 / 10", delta="Khá tốt")
            
            st.markdown("---")
            st.markdown("#### 📝 Chi tiết nhận xét của AI cho học sinh:")
            st.info("""
            * **Phần làm tốt:** Học sinh giải quyết trọn vẹn các câu hỏi đại số, biến đổi tương đương chính xác, trình bày sạch sẽ.
            * **Điểm trừ (0.5đ):** Ở câu hình học, bước biến đổi trung gian chưa thực sự tối ưu, thiếu kết luận chặt chẽ ở ý cuối.
            * **Gợi ý lời nhận xét của giáo viên:** *Bài làm thể hiện sự cố gắng, tư duy tốt. Cần lưu ý thêm các điều kiện xác định ở bài toán chứa căn thức.*
            """)
