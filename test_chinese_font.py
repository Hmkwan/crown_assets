#!/usr/bin/env python3
"""测试中文字体渲染"""

from PIL import Image, ImageDraw, ImageFont
import os
import tempfile

def test_chinese_font():
    """测试生成带中文的图片"""
    print("开始测试中文字体渲染...")
    
    # 创建测试图片
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # 可能的字体路径
    font_paths = [
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        'C:\\Windows\\Fonts\\msyh.ttc',  # Windows 微软雅黑
        'Arial.ttf'
    ]
    
    # 尝试加载字体
    font = None
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, 40)
                print(f"✓ 成功加载字体: {font_path}")
                break
            except Exception as e:
                print(f"✗ 加载字体失败 {font_path}: {e}")
    
    if font is None:
        print("✗ 未找到任何可用的中文字体!")
        return False
    
    # 绘制中文文本
    test_text = "设备名称: 测试设备\n设备编号: EQ-2024-001\n位置: 办公室"
    y = 50
    for line in test_text.split('\n'):
        draw.text((50, y), line, font=font, fill='black')
        y += 60
    
    # 保存测试图片（写到临时目录）
    output_path = os.path.join(tempfile.gettempdir(), 'test_chinese_font.png')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"✓ 测试图片已保存: {output_path}")
    
    return True

if __name__ == '__main__':
    success = test_chinese_font()
    exit(0 if success else 1)
