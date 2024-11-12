import os
from PIL import Image, ImageDraw, ImageFont
import piexif
import json


# สร้างไฟล์เก็บข้อมูลกล้อง
CACHE_FILE = 'camera_info_cache.json'

# ฟังก์ชันสำหรับดึงข้อมูล EXIF
def get_exif_data(image):
    exif_data = {}
    try:
        exif_raw = image.info.get('exif')
        if exif_raw:
            exif_dict = piexif.load(exif_raw)
            exif_data['camera'] = exif_dict['0th'].get(piexif.ImageIFD.Make, b'').decode('utf-8')
            exif_data['model'] = exif_dict['0th'].get(piexif.ImageIFD.Model, b'').decode('utf-8')
            exif_data['focal_length'] = exif_dict['Exif'].get(piexif.ExifIFD.FocalLength, None)
            exif_data['f_stop'] = exif_dict['Exif'].get(piexif.ExifIFD.FNumber, None)
            exif_data['exposure_time'] = exif_dict['Exif'].get(piexif.ExifIFD.ExposureTime, None)
            exif_data['iso'] = exif_dict['Exif'].get(piexif.ExifIFD.ISOSpeedRatings, None)
    except Exception as e:
        print(f"Error reading EXIF data: {e}")
    return exif_data

# ฟังก์ชันสำหรับถามข้อมูลจากผู้ใช้
def prompt_for_missing_info(image_name, exif_data):
    cached_info = load_cached_info()

    if cached_info:
        print(f"Previous camera info: {cached_info}")
        confirm = input("Is this the same camera info as before? (y/n): ")
        if confirm.lower() == 'y':
            return cached_info

    print(f"Missing EXIF data for {image_name}. Please provide the following details:")
    camera = input("Enter camera make/model (e.g., iPhone 11 Pro Max): ")
    focal_length = input("Enter focal length in mm (e.g., 26): ")
    f_stop = input("Enter f-stop (e.g., 1.8): ")
    exposure_time = input("Enter exposure time (e.g., 1/172): ")
    iso = input("Enter ISO (e.g., 32): ")

    new_info = {
        'camera': camera,
        'focal_length': focal_length,
        'f_stop': f_stop,
        'exposure_time': exposure_time,
        'iso': iso
    }
    save_cached_info(new_info)

    return new_info

# ฟังก์ชันสำหรับบันทึกข้อมูลกล้องลง cache
def save_cached_info(info):
    with open(CACHE_FILE, 'w') as cache_file:
        json.dump(info, cache_file)

# ฟังก์ชันสำหรับโหลดข้อมูลกล้องจาก cache
def load_cached_info():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as cache_file:
            return json.load(cache_file)
    return None

# ฟังก์ชันสำหรับเพิ่มกรอบและข้อความลงในภาพ
def add_text_to_image(image_path, output_folder):
    print(f"Processing {image_path}...")
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image {image_path}: {e}")
        return

    exif_data = get_exif_data(image)

    if not exif_data.get('camera'):
        exif_data = prompt_for_missing_info(os.path.basename(image_path), exif_data)

    camera = exif_data.get('camera', 'Unknown Camera')
    focal_length = exif_data.get('focal_length', 'Unknown mm')
    f_stop = exif_data.get('f_stop', 'Unknown f-stop')
    exposure_time = exif_data.get('exposure_time', 'Unknown exposure')
    iso = exif_data.get('iso', 'Unknown ISO')

    text_bold = f"Shot on {camera}"
    text_regular = f"{focal_length}mm f/{f_stop} {exposure_time}s. ISO {iso}" #ปรินท์

    draw = ImageDraw.Draw(image)

    # ดึงค่าจาก environment variables
    font_path_bold = os.getenv('FONT_BOLD_PATH', 'D:/ig/frame add/front/AnonymousPro-Bold.ttf')
    font_path_regular = os.getenv('FONT_REGULAR_PATH', 'D:/ig/frame add/front/AnonymousPro-Regular.ttf')

# ตรวจสอบว่าฟอนต์ถูกต้อง
    if not os.path.exists(font_path_bold) or not os.path.exists(font_path_regular):
        print("Error: Font file not found.")
        return
    
    # ใช้ค่าคงที่สำหรับกรอบล่าง
    
    fixed_bottom_border_height_percentage = float(os.getenv('BOTTOM_BORDER_HEIGHT', 10))  # ค่าเริ่มต้น 10%
    border_width = int(image.width * (float(os.getenv('BORDER_WIDTH', 2)) / 100))  # ใช้ค่าจาก environment variable
    bottom_border_height = int(image.height * (fixed_bottom_border_height_percentage / 100))
    # ใช้ค่าจาก environment variables
    font_bold_size = int(image.height * (float(os.getenv('FONT_BOLD_SIZE', 3)) / 100))  # 3% ของความสูงภาพ
    font_regular_size = int(image.height * (float(os.getenv('FONT_REGULAR_SIZE', 2)) / 100))  # 2% ของความสูงภาพ 
    font_bold = ImageFont.truetype(font_path_bold, font_bold_size)
    font_regular = ImageFont.truetype(font_path_regular, font_regular_size)

   # วาดกรอบ
    draw.rectangle([0, 0, image.width, image.height], outline="black", width=border_width)
    draw.rectangle([0, image.height - bottom_border_height, image.width, image.height], fill="black")   

    text_bbox_bold = draw.textbbox((0, 0), text_bold, font=font_bold)
    text_bbox_regular = draw.textbbox((0, 0), text_regular, font=font_regular)

    text_width_bold = text_bbox_bold[2] - text_bbox_bold[0]
    text_height_bold = text_bbox_bold[3] - text_bbox_bold[1]

    text_width_regular = text_bbox_regular[2] - text_bbox_regular[0]
    text_height_regular = text_bbox_regular[3] - text_bbox_regular[1]
    line_spacing = text_height_regular * 0.6  #  ค่าความห่างระหว่างบรรทัด
    text_x_bold = (image.width - text_width_bold) / 2
    text_y_bold = image.height - bottom_border_height + (bottom_border_height - text_height_bold - text_height_regular - line_spacing) / 2
    draw.text((text_x_bold, text_y_bold), text_bold, fill="white", font=font_bold)
    draw.text((text_x_bold, text_y_bold), text_bold, fill="white", font=font_bold)
    text_x_regular = (image.width - text_width_regular) / 2
    text_y_regular = text_y_bold + text_height_bold + line_spacing
    draw.text((text_x_regular, text_y_regular), text_regular, fill="white", font=font_regular)

    output_path = os.path.join(output_folder, os.path.basename(image_path))
    try:
        image.save(output_path, "JPEG")
        print(f"Saved image to {output_path}")
    except Exception as e:
        print(f"Error saving image {output_path}: {e}")

# ฟังก์ชันหลักสำหรับประมวลผลภาพในโฟลเดอร์
def process_images(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(input_folder, filename)
            add_text_to_image(image_path, output_folder)

input_folder = 'D:/ig/frame add/images'
output_folder = 'D:/ig/frame add/output_images'

os.makedirs(output_folder, exist_ok=True)

process_images(input_folder, output_folder)
