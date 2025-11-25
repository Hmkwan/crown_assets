"""
二维码生成工具模块
用于生成资产/配件的二维码标签
"""
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import base64


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
                         department=None, size_mm=(70, 70), dpi=300):
    """
    生成资产标签（70*70mm）
    
    Args:
        asset_type: 资产类型 ('equipment' 或 'spare_part')
        asset_id: 资产ID
        asset_name: 资产名称
        asset_code: 资产编码/序列号
        department: 所属部门（可选）
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
    
    # 计算边距和区域
    margin = int(width_px * 0.05)  # 5%边距
    qr_size = int(width_px * 0.5)  # 二维码占50%宽度
    text_area_height = height_px - qr_size - margin * 3
    
    # 生成二维码数据（包含资产信息）
    qr_data = f"{asset_type}:{asset_id}:{asset_code}"
    qr_img = generate_qrcode(qr_data, size=qr_size, border=1)
    
    # 粘贴二维码（居中，顶部）
    qr_x = (width_px - qr_size) // 2
    qr_y = margin
    img.paste(qr_img, (qr_x, qr_y))
    
    # 尝试加载字体（如果系统有中文字体）
    font_large = None
    font_medium = None
    font_small = None
    
    # 尝试加载中文字体（Windows）
    font_paths = [
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
        "C:/Windows/Fonts/simsun.ttc",  # 宋体
        "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
    ]
    
    for font_path in font_paths:
        try:
            font_large = ImageFont.truetype(font_path, int(height_px * 0.08))
            font_medium = ImageFont.truetype(font_path, int(height_px * 0.06))
            font_small = ImageFont.truetype(font_path, int(height_px * 0.05))
            break
        except:
            continue
    
    # 如果没有找到中文字体，尝试使用系统默认字体
    if font_large is None:
        try:
            font_large = ImageFont.truetype("arial.ttf", int(height_px * 0.08))
            font_medium = ImageFont.truetype("arial.ttf", int(height_px * 0.06))
            font_small = ImageFont.truetype("arial.ttf", int(height_px * 0.05))
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
    
    # 绘制文本信息
    text_y = qr_y + qr_size + margin
    
    # 资产名称（大字体）
    text_lines = []
    # 自动换行处理长名称
    max_width = width_px - margin * 2
    words = asset_name
    if len(words) > 8:  # 如果名称太长，截断
        words = words[:8] + "..."
    text_lines.append(('名称', words))
    
    # 资产编码
    text_lines.append(('编码', asset_code))
    
    # 部门（如果有）
    if department:
        text_lines.append(('部门', department))
    
    # 绘制文本
    line_height = int(height_px * 0.07)
    for i, (label, value) in enumerate(text_lines):
        y_pos = text_y + i * line_height
        if y_pos + line_height > height_px - margin:
            break
        
        # 标签
        draw.text((margin, y_pos), f"{label}:", fill='black', font=font_small)
        # 值
        draw.text((margin + int(width_px * 0.15), y_pos), value, fill='black', font=font_medium)
    
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

