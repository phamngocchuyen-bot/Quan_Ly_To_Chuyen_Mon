import streamlit as st
import pandas as pd

# Cấu hình giao diện trang web
st.set_page_config(
    page_title="Quản lý Tổ Chuyên Môn Toán - Tin",
    page_icon="📚",
    layout="wide"
)

st.title("📊 Hệ thống Quản lý Tổ Chuyên Môn Toán - Tin")
st.markdown("Trang web điều hành, theo dõi thời khóa biểu, tiến độ ra đề, chuyên đề và soạn bài của giáo viên trong tổ.")

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
    
    st.markdown("---")
    st.info("💡 **Mẹo:** Bạn có thể chọn các mục bên menu trái để xem chi tiết thời khóa biểu hoặc phân công nhiệm vụ cụ thể cho từng thành viên.")

# --- CHỨC NĂNG 2: THỜI KHÓA BIỂU & GIỜ DẠY ---
elif menu == "📅 Thời khóa biểu & Giờ dạy":
    st.subheader("Quản lý Thời khóa biểu & Giờ chuẩn quy đổi")
    
    # Dữ liệu mẫu (sau này bạn có thể thay bằng kết nối Google Sheets thực tế)
    data_ns = {
        "Giáo viên": ["Nguyễn Văn An", "Trần Thị Bình", "Lê Hoàng Cường", "Phạm Thị Dung"],
        "Số tiết TKB/Tuần": [18, 20, 16, 19],
        "Nhiệm vụ kiêm nhiệm": ["Chủ nhiệm lớp 10", "Bồi dưỡng HSG", "Phòng bộ môn", "Đoàn thanh niên"],
        "Giờ chuẩn quy đổi": [22.5, 26.0, 20.0, 23.5],
        "Trạng thái": ["Đạt chuẩn", "Đạt chuẩn", "Đạt chuẩn", "Đạt chuẩn"]
    }
    df_ns = pd.DataFrame(data_ns)
    st.dataframe(df_ns, use_container_width=True)

# --- CHỨC NĂNG 3: QUẢN LÝ NHIỆM VỤ ---
elif menu == "📝 Quản lý Nhiệm vụ":
    st.subheader("Theo dõi tiến độ: Ra đề, Chuyên đề, Soạn bài")
    
    data_nv = {
        "Loại nhiệm vụ": ["Ra đề", "Chuyên đề", "Soạn bài", "Ra đề"],
        "Nội dung chi tiết": ["Đề kiểm tra giữa kỳ II - Toán 10", "Ứng dụng hàm số bậc hai thực tế", "Giáo án STEM: Mô hình cầu", "Đề kiểm tra đại số 11"],
        "Người thực hiện": ["Nguyễn Văn An", "Trần Thị Bình", "Lê Hoàng Cường", "Phạm Thị Dung"],
        "Hạn nộp": ["30/03/2026", "05/04/2026", "10/04/2026", "15/04/2026"],
        "Trạng thái": ["Đã duyệt AI", "Chờ rà soát", "Đang thực hiện", "Hoàn thành"]
    }
    df_nv = pd.DataFrame(data_nv)
    st.dataframe(df_nv, use_container_width=True)
    
    with st.expander("➕ Thêm nhiệm vụ mới cho giáo viên"):
        with st.form("form_them_nhiem_vu"):
            giao_vien = st.selectbox("Chọn giáo viên", ["Nguyễn Văn An", "Trần Thị Bình", "Lê Hoàng Cường", "Phạm Thị Dung"])
            loai = st.selectbox("Loại nhiệm vụ", ["Ra đề", "Chuyên đề", "Soạn bài"])
            noi_dung = st.text_input("Nội dung chi tiết nhiệm vụ")
            han_nop = st.date_input("Hạn hoàn thành")
            submit = st.form_submit_button("Lưu nhiệm vụ")
            if submit:
                st.success(f"Đã phân công thành công nhiệm vụ cho thầy/cô {giao_vien}!")

# --- CHỨC NĂNG 4: TRỢ LÝ AI ---
elif menu == "🤖 Trợ lý AI Kiểm tra tài liệu":
    st.subheader("Trợ lý AI tự động rà soát đề thi và bài soạn")
    st.write("Tải lên file tài liệu (đề thi, ma trận, giáo án) để AI tự động kiểm tra cấu trúc và góp ý.")
    
    uploaded_file = st.file_uploader("Chọn file văn bản (.docx, .pdf)", type=["docx", "pdf", "txt"])
    if uploaded_file is not None:
        if st.button("🚀 Bắt đầu phân tích bằng AI"):
            with st.spinner("AI đang đọc và phân tích tài liệu..."):
                import time
                time.sleep(2) # Giả lập thời gian AI xử lý
            st.success("Phân tích hoàn tất!")
            st.markdown("### Kết quả đánh giá từ AI:")
            st.info("✅ **Cấu trúc ma trận:** Đúng chuẩn tỷ lệ Nhận biết (40%), Thông hiểu (30%), Vận dụng (30%).\n\n⚠️ **Gợi ý cải thiện:** Câu hỏi số 8 cần điều chỉnh lại từ ngữ để rõ nghĩa hơn đối với học sinh.")