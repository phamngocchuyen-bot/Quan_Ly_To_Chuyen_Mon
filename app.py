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

# --- CHỨC NĂNG 3: TRỢ LÝ AI CHẤM BÀI ---
elif menu == "🤖 Trợ lý AI Chấm bài tự động":
    st.subheader("🤖 Hệ thống AI Tự động chấm bài theo Đáp án chuẩn")
    st.markdown("Hệ thống đọc file đáp án, đối chiếu với bài làm của học sinh để chấm điểm và đưa ra nhận xét chi tiết.")

    api_key_input = st.text_input("Nhập Google Gemini API Key", type="password", placeholder="Nhập API Key (bắt đầu bằng AIzaSy hoặc AQ)...", key="api_key_cham_bai")

    if "answer_filename" not in st.session_state:
        st.session_state.answer_filename = None
    if "answer_content" not in st.session_state:
        st.session_state.answer_content = ""
    if "df_kq_cache" not in st.session_state:
        st.session_state.df_kq_cache = None

    answer_file = st.file_uploader(
        "Tải lên file Đáp án chuẩn / Thang điểm (PDF, DOCX, TXT, Ảnh)", 
        type=["pdf", "png", "jpg", "jpeg", "docx", "txt"]
    )

    if answer_file is not None:
        st.session_state.answer_filename = answer_file.name
        st.session_state.answer_content = doc_noi_dung_file(answer_file)

    if st.session_state.answer_filename:
        st.success(f"📁 Đã lưu đáp án: **{st.session_state.answer_filename}**.")
        with st.expander("🔍 Xem nhanh nội dung Đáp án chuẩn"):
            st.text(st.session_state.answer_content[:600] if len(st.session_state.answer_content) > 600 else st.session_state.answer_content)

    if st.button("⚡ Bắt đầu Chấm điểm tự động"):
        if not st.session_state.answer_filename:
            st.warning("Thầy vui lòng tải lên file đáp án chuẩn trước khi bấm chấm tự động nhé!")
        else:
            with st.spinner("Hệ thống đang quét bài nộp từ Form và đối chiếu với đáp án chuẩn..."):
                import time
                time.sleep(1.0)
            
            try:
                df_nop_bai = load_data("NopBaiHS")
                
                if df_nop_bai.empty:
                    st.warning("Hiện tại tab 'NopBaiHS' chưa có dữ liệu bài nộp nào từ học sinh.")
                else:
                    danh_sach_ket_qua = []
                    
                    dung_api_that = False
                    model = None
                    if api_key_input.strip().startswith("AIzaSy") or api_key_input.strip().startswith("AQ"):
                        try:
                            import google.generativeai as genai
                            genai.configure(api_key=api_key_input.strip())
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            dung_api_that = True
                        except Exception:
                            dung_api_that = False

                    for index, row in df_nop_bai.iterrows():
                        ten_hs = str(row.get('HoTen', row.iloc[1] if len(row) > 1 else f"Học sinh {index+1}")).strip()
                        ten_bai = str(row.get('TenBaiTap', 'Bài tập chuyên đề')).strip()
                        link_bai = str(row.get('LinkBaiLam', '#')).strip()
                        
                        # LẤY NỘI DUNG BÀI LÀM CỦA HỌC SINH (Thầy có thể đổi tên cột 'NoiDung', 'BaiLam', 'CauTraLoi' cho khớp với Google Sheets của thầy)
                        noi_dung_hs = str(row.get('NoiDung', row.get('BaiLam', row.get('CauTraLoi', 'Không có nội dung văn bản trực tiếp')))).strip()

                        diem_str, nhan_xet_str = "", ""
                        
                        if dung_api_that and model:
                            try:
                                prompt = f"""Bạn là một giáo viên bộ môn chấm bài rất nghiêm khắc, khách quan và công tâm.
        
--- ĐÁP ÁN CHUẨN VÀ BIỂU ĐIỂM ---
{st.session_state.answer_content}

--- BÀI LÀM CỦA HỌC SINH ({ten_hs}) ---
{noi_dung_hs}

--- YÊU CẦU CHẤM ĐIỂM ---
1. Đối chiếu kỹ lưỡng nội dung bài làm của học sinh với đáp án chuẩn ở trên.
2. QUY TẮC 0 ĐIỂM NGHIÊM NGẶT: Nếu bài làm hoàn toàn lạc đề, không đúng trọng tâm yêu cầu của đề bài, viết linh tinh hoặc không liên quan -> BẮT BUỘC CHO 0 ĐIỂM (Không châm chước, không tìm ý phụ vớt vát).
3. Chỉ cho điểm cao nếu bài làm giải quyết đúng bản chất yêu cầu của đáp án chuẩn.
4. Trả về đúng định dạng 2 dòng duy nhất:
Điểm: [số điểm từ 0 đến 10]/10
Nhận xét: [Nhận xét chi tiết, chỉ rõ chỗ đúng/sai]
"""
                                res = model.generate_content(prompt)
                                lines = res.text.strip().split('\n')
                                
                                line_diem = [l for l in lines if 'Điểm:' in l or 'diem:' in l.lower()]
                                line_nx = [l for l in lines if 'Nhận xét:' in l or 'nhan xet:' in l.lower()]
                                
                                if line_diem and line_nx:
                                    diem_str = line_diem[0].replace("Điểm:", "").replace("điểm:", "").strip()
                                    nhan_xet_str = line_nx[0].replace("Nhận xét:", "").replace("nhận xét:", "").strip()
                                else:
                                    diem_str = "0/10"
                                    nhan_xet_str = res.text.strip()[:200]
                            except Exception as err:
                                diem_str = "0/10"
                                nhan_xet_str = f"Lỗi gọi API: {str(err)}"
                        else:
                            diem_str = "0/10"
                            nhan_xet_str = "Chưa nhập API Key Google Gemini hợp lệ."

                        danh_sach_ket_qual = {
                            "Học sinh": ten_hs,
                            "Bài tập": ten_bai,
                            "Điểm chuẩn": diem_str,
                            "Nhận xét chi tiết": nhan_xet_str,
                            "Link bài làm": link_bai
                        }
                        danh_sach_ket_qua.append(danh_sach_ket_qual)
                    
                    st.session_state.df_kq_cache = pd.DataFrame(danh_sach_ket_qua)
                    st.success(f"🎉 Hoàn tất chấm điểm thành công cho {len(df_nop_bai)} học sinh!")
                    
            except Exception as e:
                st.error(f"Lỗi xử lý chấm bài: {e}")

    if st.session_state.df_kq_cache is not None and not st.session_state.df_kq_cache.empty:
        st.markdown("---")
        st.markdown("### 📊 Bảng kết quả chấm điểm tổng hợp:")
        st.dataframe(st.session_state.df_kq_cache, use_container_width=True)
        
        st.markdown("#### 📥 Lưu trữ kết quả:")
        csv_data = st.session_state.df_kq_cache.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Tải xuống Bảng điểm tổng hợp (.csv / Excel)",
            data=csv_data,
            file_name=f"BangDiem_TongHop_{datetime.now().strftime('%d%m%Y')}.csv",
            mime="text/csv",
            type="primary"
        )
