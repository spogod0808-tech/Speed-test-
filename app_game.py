import streamlit as str_web
from streamlit_drawable_canvas import st_canvas
import easyocr
from PIL import Image
import numpy as np
import time
import random

# 1. Cấu hình tiêu đề trang web
str_web.set_page_config(page_title="Handwriting Speed Test", layout="centered")
str_web.title("✍️ Handwriting Speed Test & AI OCR")

# 2. Tải bộ não AI (Lưu vào bộ nhớ cache để không bị tải lại mỗi lần vẽ)
@str_web.cache_resource
def load_ai():
    return easyocr.Reader(['en'])

reader = load_ai()

# 3. Ngân hàng từ vựng tiếng Anh
if "target_phrase" not in str_web.session_state:
    danh_sach_cau = [
        "Hello world", "Artificial intelligence", "Machine learning", 
        "Open source software", "Computer vision", "Speed test game", 
        "Have a nice day", "Keep moving forward"
    ]
    str_web.session_state.target_phrase = random.choice(danh_sach_cau)

# Hiển thị từ thách thức
str_web.info(f"👉 **Please write this phrase:** `{str_web.session_state.target_phrase}`")

# Nút đổi câu khác
if str_web.button("🔄 Next Phrase"):
    danh_sach_cau = [
        "Hello world", "Artificial intelligence", "Machine learning", 
        "Open source software", "Computer vision", "Speed test game", 
        "Have a nice day", "Keep moving forward"
    ]
    str_web.session_state.target_phrase = random.choice(danh_sach_cau)
    str_web.rerun()

# 4. Tạo bảng vẽ Canvas thông minh
str_web.write("---")
str_web.write("### 👇 Draw your handwriting here:")

# Ghi nhận thời gian bắt đầu vẽ
if "start_time" not in str_web.session_state:
    str_web.session_state.start_time = time.time()

canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0)",
    stroke_width=6,
    stroke_color="#000000",
    background_color="#FFFFFF", # Lót nền trắng sẵn từ gốc, không lo lỗi ảnh đen!
    height=250,
    width=700,
    drawing_mode="freedraw",
    key="canvas",
)

# 5. Xử lý khi người dùng vẽ xong (AI tự động chấm điểm)
if canvas_result.image_data is not None:
    # Lấy dữ liệu ảnh từ bảng vẽ
    img_array = canvas_result.image_data
    
    # Kiểm tra xem người dùng có thực sự vẽ gì không (tránh bảng trắng)
    if np.any(img_array[:, :, 3] > 0): 
        # Đo thời gian hoàn thành
        duration = time.time() - str_web.session_state.start_time
        
        str_web.write("⏳ *AI is analyzing your handwriting...*")
        
        # Chuyển ảnh sang dạng PIL để AI đọc
        image = Image.fromarray(img_array.astype('uint8'), 'RGBA').convert('RGB')
        image.save("temp_draw.jpg")
        
        # Đưa vào bộ não AI đọc chữ
        result = reader.readtext("temp_draw.jpg")
        chu_ai_doc = " ".join([line[1] for line in result]).strip()
        
        if not chu_ai_doc:
            hien_thi = "[Can't read any words]"
        else:
            hien_thi = chu_ai_doc
            
        str_web.success(f"🤖 **AI Detected:** `{hien_thi}`")
        
        # Tính toán tốc độ WPM
        so_tu = len([w for w in chu_ai_doc.split() if w])
        if so_tu > 0 and duration > 0:
            wpm = (so_tu / duration) * 60
            
            # Tính độ chính xác
            target = str_web.session_state.target_phrase.lower().strip()
            user_input = chu_ai_doc.lower().strip()
            
            if target == user_input:
                accuracy = 100
            else:
                target_words = target.split()
                input_words = user_input.split()
                correct = sum(1 for w in input_words if w in target_words)
                accuracy = round((correct / len(target_words)) * 100)
            
            # Hiển thị số liệu siêu đẹp bằng cột (Columns)
            col1, col2, col3 = str_web.columns(3)
            col1.metric("Duration", f"{duration:.2f} sec")
            col2.metric("Writing Speed", f"{int(wpm)} WPM")
            col3.metric("Accuracy", f"{accuracy}%")
            
    else:
        # Nếu bảng trống, reset lại thời gian bắt đầu
        str_web.session_state.start_time = time.time()