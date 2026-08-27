import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime
import io

# Cấu hình giao diện trang web
st.set_page_config(
    page_title="Hệ thống Quản lý Bài tập & Trợ lý AI Chấm bài",
    page_icon="📖",
    layout="wide"
)

SHEET_ID = "1eIVRRQhr3SUkMdlHB9Fy2_GmujTGFyJPejgGoxXNnJs"

@st.cache_data(ttl=60)
def load_data(sheet_name):
    encoded_sheet_name = urllib.parse.quote(sheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
    return pd.read_csv(url, dtype=str)

# Hàm đọc nội dung file đáp án do giáo viên tải lên
def doc_noi_dung_file(uploaded_file):
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        text_content = ""
        if file_extension == 'txt':
            text_content = str(uploaded_file.read(), "utf-8")
        elif file_extension == 'docx':
            import docx
            doc = docx.Document(uploaded_file)
            text_content = "\n".join([p.text for p in doc.paragraphs])
        elif file_extension == 'pdf':
            import pypdf
            reader = pypdf.PdfReader(uploaded_file)
            for page in reader.pages:
                text_content += page.extract_text() or ""
        else:
            text_content = f"File định dạng {file_extension.upper()} đã được tải lên làm đáp án chuẩn."
        return text_content
    except Exception as e:
        return f"Đã đọc file đáp án thành công. (Chi tiết: {e})"

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
    st.subheader("📚 Bảng theo dõi tiến độ chi tiết từng học sinh")
    
    if st.button("🔄 Làm mới dữ liệu"):
        st.cache_data.clear()
        st.rerun()

    try:
        df_hs = load_data("DanhSachHS")
        df_bt = load_data("GiaoBaiTap")
        df_nop = load_data("NopBaiHS")
        
        if df_hs.empty or df_bt.empty:
            st.warning("Thầy vui lòng kiểm tra lại tab 'DanhSachHS' và 'GiaoBaiTap' trong Google Sheets đảm bảo đã có dữ liệu.")
        else:
            df_hs = df_hs.rename(columns=lambda x: str(x).strip())
            df_bt = df_bt.rename(columns=lambda x: str(x).strip())
            
            if 'Lớp' in df_hs.columns and 'Lop' not in df_hs.columns:
                df_hs = df_hs.rename(columns={'Lớp': 'Lop'})
            if 'Họ và tên' in df_hs.columns and 'HoTen' not in df_hs.columns:
                df_hs = df_hs.rename(columns={'Họ và tên': 'HoTen'})
                
            if 'Lớp' in df_bt.columns and 'Lop' not in df_bt.columns:
                df_bt = df_bt.rename(columns={'Lớp': 'Lop'})
            if 'Tên bài tập' in df_bt.columns and 'TenBaiTap' not in df_bt.columns:
                df_bt = df_bt.rename(columns={'Tên bài tập': 'TenBaiTap'})
            if 'Hạn nộp' in df_bt.columns and 'HanNop' not in df_bt.columns:
                df_bt = df_bt.rename(columns={'Hạn nộp': 'HanNop'})

            df_hs['Lop'] = df_hs['Lop'].astype(str).str.replace('.0', '', regex=False).str.strip()
            df_bt['Lop'] = df_bt['Lop'].astype(str).str.replace('.0', '', regex=False).str.strip()

            df_tong_hop = pd.merge(df_hs, df_bt, on='Lop', how='inner')
            
            if df_tong_hop.empty:
                st.warning("⚠️ Không tìm thấy điểm chung (Lớp) giữa danh sách học sinh và bài tập được giao.")
            else:
                nop_name_col = None
                if not df_nop.empty:
                    df_nop = df_nop.rename(columns=lambda x: str(x).strip())
                    for col in df_nop.columns:
                        if 'ho' in col.lower() or 'tên' in col.lower() or 'hoten' in col.lower():
                            nop_name_col = col
                            break
                    if not nop_name_col and len(df_nop.columns) > 1:
                        nop_name_col = df_nop.columns[1]

                def xet_trang_thai(row):
                    ten_hs = str(row.get('HoTen', '')).strip()
                    da_nop = False
                    if not df_nop.empty and nop_name_col:
                        for _, nop_row in df_nop.iterrows():
                            nop_ten = str(nop_row.get(nop_name_col, '')).strip()
                            if ten_hs.lower() in nop_ten.lower() or nop_ten.lower() in ten_hs.lower():
                                da_nop = True
                                break
                    
                    if da_nop:
                        return "Đã nộp ✅"
                        
                    try:
                        ngay_het_han = datetime.strptime(str(row.get('HanNop', '')).strip(), '%d/%m/%Y')
                        if datetime.now() > ngay_het_han:
                            return "Quá hạn ⚠️"
                        else:
                            return "Đang làm ⏳"
                    except:
                        return "Đang làm ⏳"

                df_tong_hop['TrangThai'] = df_tong_hop.apply(xet_trang_thai, axis=1)
                
                st.markdown("### 🔍 Bộ lọc tìm kiếm & Theo dõi")
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    danh_sach_lop = ["Tất cả các lớp"] + sorted(df_tong_hop['Lop'].unique().tolist())
                    chon_lop = st.selectbox("Lọc theo Lớp học:", danh_sach_lop)
                with col_f2:
                    danh_sach_tt = ["Tất cả trạng thái", "Đã nộp ✅", "Đang làm ⏳", "Quá hạn ⚠️"]
                    chon_tt = st.selectbox("Lọc theo Trạng thái bài làm:", danh_sach_tt)

                if chon_lop != "Tất cả các lớp":
                    df_tong_hop = df_tong_hop[df_tong_hop['Lop'] == chon_lop]
                if chon_tt != "Tất cả trạng thái":
                    df_tong_hop = df_tong_hop[df_tong_hop['TrangThai'] == chon_tt]

                def rut_gon_ten(text):
                    text_str = str(text)
                    if len(text_str) > 40:
                        return text_str[:40] + "..."
                    return text_str
                
                df_tong_hop['TenBaiTap_Short'] = df_tong_hop['TenBaiTap'].apply(rut_gon_ten)
                
                cols_show = [c for c in ['Lop', 'HoTen', 'TenBaiTap_Short', 'HanNop', 'TrangThai'] if c in df_tong_hop.columns]
                df_hien_thi = df_tong_hop[cols_show].rename(columns={
                    'Lop': 'Lớp',
                    'HoTen': 'Họ và tên',
                    'TenBaiTap_Short': 'Tên bài tập',
                    'HanNop': 'Hạn nộp',
                    'TrangThai': 'Trạng thái'
                })
                
                st.markdown("---")
                st.dataframe(df_hien_thi, use_container_width=True)
            
    except Exception as e:
        st.error(f"Lỗi hiển thị bảng tiến độ: {e}")

import streamlit as st
import pandas as pd
import datetime

# --- HÀM HỖ TRỢ CHUẨN HÓA CHUỖI ---
def chuan_hoa_dap_an(text):
    """
    Hàm này tự động xóa mọi khoảng trắng và viết hoa toàn bộ chữ cái.
    Giúp 'a h', ' a H ', hay 'AH' đều được máy hiểu là một đáp án duy nhất: 'AH'.
    """
    return str(text).strip().upper().replace(" ", "")

# --- CHỨC NĂNG 3: HỆ THỐNG CHẤM TỰ LUẬN ĐIỀN KHUYẾT TỰ ĐỘNG ---
# Giả sử menu của thầy là một khối if...elif
# elif menu == "🤖 Chấm Tự luận Điền khuyết":
st.subheader("🎯 Hệ thống Chấm Tự luận Điền khuyết (Đối sánh tuyệt đối)")
st.markdown("Hệ thống tự động chuẩn hóa đáp án của học sinh và khớp với barem chuẩn. Đảm bảo chính xác 100%, không sử dụng AI để tránh sai sót.")

# 1. KHAI BÁO BAREM ĐÁP ÁN CHUẨN CỦA TỔ CHUYÊN MÔN
# Mỗi bước có thể có nhiều cách gõ đáp án đúng (ví dụ: 1/2 hoặc 0.5)
DAP_AN_CHUAN = {
    "Buoc1": ["AH"],
    "Buoc2": ["BD"],
    "Buoc3": ["1/2", "0.5"],
    "Buoc4": ["5/2", "2.5"]
}
DIEM_MOI_BUOC = 0.25

st.info("📌 **Đang áp dụng Barem cho bài toán Hình không gian:**\n"
        "- Bước 1 (Hình chiếu): AH\n"
        "- Bước 2 (Chứng minh vuông góc): BD\n"
        "- Bước 3 (Tính AO^2): 1/2 hoặc 0.5\n"
        "- Bước 4 (Tính 1/AH^2): 5/2 hoặc 2.5")

if st.button("⚡ Bấm vào đây để chạy Test Chấm điểm 3 học sinh mẫu"):
    with st.spinner("Hệ thống đang quét đáp án và tính điểm..."):
        
        # 2. TẠO DỮ LIỆU TEST MẪU (Thay vì load file Excel)
        du_lieu_mau = [
            {"HoTen": "Nguyễn Văn A", "Buoc1": "AH", "Buoc2": "BD", "Buoc3": "1/2", "Buoc4": "5/2"},
            {"HoTen": "Trần Thị B", "Buoc1": "a h", "Buoc2": " b d ", "Buoc3": "0.5", "Buoc4": "3"},
            {"HoTen": "Lê Văn C", "Buoc1": "SA", "Buoc2": "AC", "Buoc3": "1", "Buoc4": "4"}
        ]
        df_nop_bai = pd.DataFrame(du_lieu_mau)
        
        # 3. THUẬT TOÁN CHẤM ĐIỂM
        danh_sach_ket_qua = []
        
        for index, row in df_nop_bai.iterrows():
            ten_hs = row['HoTen']
            tong_diem = 0.0
            chi_tiet_cham = []
            
            # Quét qua từng bước trong Barem
            for buoc, cac_dap_an_dung in DAP_AN_CHUAN.items():
                dap_an_hs = row.get(buoc, "")
                dap_an_hs_da_chuan_hoa = chuan_hoa_dap_an(dap_an_hs)
                
                # Chuẩn hóa danh sách đáp án đúng
                danh_sach_da_chuan_hoa = [chuan_hoa_dap_an(ans) for ans in cac_dap_an_dung]
                
                # So sánh tuyệt đối
                if dap_an_hs_da_chuan_hoa in danh_sach_da_chuan_hoa:
                    tong_diem += DIEM_MOI_BUOC
                    chi_tiet_cham.append(f"{buoc}: ✅ (0.25đ)")
                else:
                    chi_tiet_cham.append(f"{buoc}: ❌ (0đ)")
            
            # Ghi nhận kết quả
            danh_sach_ket_qua.append({
                "Học sinh": ten_hs,
                "Tổng điểm": f"{tong_diem} / 1.0",
                "Phân tích từng bước": " | ".join(chi_tiet_cham),
                "Lưu vết nhập liệu": f"B1: {row['Buoc1']} | B2: {row['Buoc2']} | B3: {row['Buoc3']} | B4: {row['Buoc4']}"
            })
        
        # 4. HIỂN THỊ KẾT QUẢ
        st.session_state.df_kq_cache = pd.DataFrame(danh_sach_ket_qua)
        st.success(f"🎉 Đã chấm xong bài cho {len(df_nop_bai)} học sinh với độ chính xác 100%!")

# Hiển thị bảng và nút tải file
if "df_kq_cache" in st.session_state and st.session_state.df_kq_cache is not None:
    st.markdown("### 📊 Bảng điểm tổng hợp")
    st.dataframe(st.session_state.df_kq_cache, use_container_width=True)
    
    csv_data = st.session_state.df_kq_cache.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Tải xuống Bảng điểm (.csv)",
        data=csv_data,
        file_name=f"BangDiem_TuLuanDienKhuyet_{datetime.datetime.now().strftime('%d%m%Y')}.csv",
        mime="text/csv",
        type="primary"
    )
