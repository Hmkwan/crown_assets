"""
二维码生成工具模块
用于生成资产/配件的二维码标签
"""
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import base64
import os
import platform


def generate_qrcode(data, size=200, border=2):
    """
    生成二维码图片
    
    Args:
        data: 要编码的数据（字符串）
        size: 二维码尺寸（像素）
        border: 边框大小
    
    Returns:
        PIL Image 对象
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    return img


def generate_asset_label(asset_type, asset_id, asset_name, asset_code, 
                         department=None, purchase_date=None, location=None, 
                         size_mm=(70, 70), dpi=300):
    """
    生成资产标签（70*70mm）- 简洁版
    
    Args:
        asset_type: 资产类型 ('equipment' 或 'spare_part')
        asset_id: 资产ID
        asset_name: 资产名称
        asset_code: 资产编码/序列号
        department: 所属部门（可选）
        purchase_date: 采购日期（可选）
        location: 存放位置（可选）
        size_mm: 标签尺寸（毫米），默认70*70mm
        dpi: 打印分辨率，默认300dpi
    
    Returns:
        PIL Image 对象
    """
    # 转换为像素（1英寸=25.4毫米）
    width_px = int(size_mm[0] * dpi / 25.4)
    height_px = int(size_mm[1] * dpi / 25.4)
    
    # 创建画布（白色背景）
    img = Image.new('RGB', (width_px, height_px), 'white')
    draw = ImageDraw.Draw(img)
    
    # 计算边距
    margin = int(width_px * 0.04)
    
    # 绘制外边框（蓝色边框，与在线打印一致）
    border_color = '#2b7bb9'  # 蓝色边框
    draw.rectangle([(0, 0), (width_px-1, height_px-1)], outline=border_color, width=3)
    
    # 尝试加载中文字体
    font_title = None
    font_bold = None
    font_normal = None
    font_small = None
    
    # 字体尺寸（增大字体）
    title_size = int(height_px * 0.088)    # 标题字体
    bold_size = int(height_px * 0.080)     # 名称字体（加大）
    normal_size = int(height_px * 0.070)   # 普通字体（加大）
    small_size = int(height_px * 0.058)    # 小字体
    
    # 根据运行环境选择字体路径
    is_windows = platform.system() == 'Windows'
    
    if is_windows:
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/msyhbd.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
        ]
    else:
        font_paths = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]
    
    font_loaded = False
    for font_path in font_paths:
        if not os.path.exists(font_path):
            continue
        try:
            font_title = ImageFont.truetype(font_path, title_size)
            font_bold = ImageFont.truetype(font_path, bold_size)
            font_normal = ImageFont.truetype(font_path, normal_size)
            font_small = ImageFont.truetype(font_path, small_size)
            font_loaded = True
            break
        except:
            continue
    
    if not font_loaded:
        try:
            font_title = ImageFont.truetype("arial.ttf", title_size)
            font_bold = ImageFont.truetype("arialbd.ttf", bold_size)
            font_normal = ImageFont.truetype("arial.ttf", normal_size)
            font_small = ImageFont.truetype("arial.ttf", small_size)
        except:
            font_title = ImageFont.load_default()
            font_bold = ImageFont.load_default()
            font_normal = ImageFont.load_default()
            font_small = ImageFont.load_default()
    
    # 顶部标题
    title_text = "设备标签" if asset_type == 'equipment' else "配件标签"
    title_y = margin + 5
    
    try:
        bbox = draw.textbbox((0, 0), title_text, font=font_bold)
        title_width = bbox[2] - bbox[0]
    except:
        title_width = len(title_text) * int(height_px * 0.04)
    
    title_x = (width_px - title_width) // 2
    draw.text((title_x, title_y), title_text, fill='#000000', font=font_bold)
    
    # 标题下方位置（不绘制分隔线）
    title_bottom = title_y + int(height_px * 0.085)
    
    # 生成二维码（与在线打印一致的尺寸）
    qr_data = f"{asset_type}:{asset_id}:{asset_code}"
    qr_size = int(width_px * 0.285)  # 调整为28.5%，与在线打印一致
    qr_img = generate_qrcode(qr_data, size=qr_size, border=1)
    
    # 文本区域（左侧）
    text_x = margin + 10
    text_y = title_bottom + int(margin * 2)
    
    # 设备名称（显示更多字符）
    if len(asset_name) <= 10:
        name_display = asset_name
    else:
        name_display = asset_name[:9] + '.'
    
    # 准备信息列表
    info_items = [
        ('name', name_display, font_bold, '#000000'),
        ('编码', asset_code if len(asset_code) <= 12 else asset_code[:11] + '.', font_normal, '#000000'),
        ('部门', department if department and len(department) <= 8 else (department[:7] + '.' if department and len(department) > 8 else '未分配'), font_normal, '#000000'),
        ('采购', purchase_date.strftime('%Y-%m-%d') if purchase_date and not isinstance(purchase_date, str) else (purchase_date if purchase_date else '未录入'), font_normal, '#000000'),
        ('位置', location if location and len(location) <= 8 else (location[:7] + '.' if location and len(location) > 8 else '未指定'), font_normal, '#000000'),
    ]
    
    # 绘制信息
    current_y = text_y + 5
    line_spacing = int(height_px * 0.098)  # 调整行间距
    
    for idx, item in enumerate(info_items):
        if item[0] == 'name':
            draw.text((text_x, current_y), item[1], fill=item[3], font=item[2])
            current_y += line_spacing + 8
        else:
            label_text = f"{item[0]}:"
            full_text = label_text + item[1]
            draw.text((text_x, current_y), full_text, fill=item[3], font=item[2])
            current_y += line_spacing
    
    # 二维码位置（右侧，与"位置"信息对齐）
    # 调整到与位置行对齐
    qr_y = text_y + 5 + line_spacing + 8 + line_spacing * 3  # 对齐到"位置"那一行
    qr_x = width_px - margin - qr_size - 8
    
    # 二维码边框（无边框，与在线打印一致）
    # draw.rectangle(
    #     [(qr_x - 1, qr_y - 1), (qr_x + qr_size + 1, qr_y + qr_size + 1)],
    #     outline='#999999',
    #     width=1
    # )
    
    # 粘贴二维码
    img.paste(qr_img, (qr_x, qr_y))
    
    # 底部信息位置（不绘制分隔线）
    footer_y = height_px - int(height_px * 0.095)
    
    # 底部信息
    bottom_y = footer_y + int(margin * 0.5)
    icon_text = "设备" if asset_type == 'equipment' else "配件"
    draw.text((margin + 8, bottom_y), icon_text, fill='#95a5a6', font=font_small)
    
    id_text = f"ID:{asset_id}"
    try:
        bbox = draw.textbbox((0, 0), id_text, font=font_small)
        id_width = bbox[2] - bbox[0]
    except:
        id_width = len(id_text) * int(height_px * 0.02)
    
    id_x = width_px - margin - id_width - 8
    draw.text((id_x, bottom_y), id_text, fill='#95a5a6', font=font_small)
    
    return img


def image_to_base64(img, format='PNG'):
    """
    将PIL图片转换为base64字符串（用于在线预览）
    
    Args:
        img: PIL Image 对象
        format: 图片格式
    
    Returns:
        base64编码的字符串
    """
    buffer = BytesIO()
    img.save(buffer, format=format)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/{format.lower()};base64,{img_str}"


def image_to_bytes(img, format='PNG'):
    """
    将PIL图片转换为字节流（用于下载）
    
    Args:
        img: PIL Image 对象
        format: 图片格式
    
    Returns:
        BytesIO 对象
    """
    buffer = BytesIO()
    img.save(buffer, format=format)
    buffer.seek(0)
    return buffer

