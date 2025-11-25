# 检查基础导入函数（示例）
def import_data(file_path):
    try:
        # Add your actual import logic here
        pass  # Remove this when adding real code
    except FileNotFoundError:
        raise Exception("导入文件不存在")
    except pd.errors.EmptyDataError:
        raise Exception("导入文件为空")
    except Exception as e:
        raise Exception(f"导入过程中发生错误: {str(e)}")

# 检查基础导出函数（示例） 
# 补充缺失的模块导入（关键修复）
import os
import pandas as pd  # 若使用pandas需保留，否则可删除
from typing import Union  # 类型提示（可选）
from urllib.parse import quote

def export_data(data: Union[str, bytes], output_path: str = None) -> bytes:
    """通用导出函数，支持字符串/字节数据导出"""
    try:
        # 统一编码为UTF-8（带BOM解决Excel乱码）
        if isinstance(data, str):
            data_bytes = data.encode('utf-8-sig')
        elif isinstance(data, bytes):
            data_bytes = data
        else:
            raise ValueError("数据类型仅支持str或bytes")

        # 处理文件输出（可选路径）
        if output_path:
            # 确保目录存在（关键修复：补充权限检查）
            dir_path = os.path.dirname(output_path)
            if dir_path and not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                except PermissionError:
                    raise Exception(f"无权限创建目录：{dir_path}")

            # 写入文件（关键修复：明确二进制写入）
            with open(output_path, 'wb') as f:
                f.write(data_bytes)

        return data_bytes
    except Exception as e:
        raise Exception(f"导出错误: {str(e)}")  # 保留原始错误信息

def content_disposition(filename: str, fallback: str = 'download.csv') -> str:
    safe = quote(filename)
    return f"attachment; filename=\"{fallback}\"; filename*=UTF-8''{safe}"

# 测试入口（补充参数校验）
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python -m app.utils.import_export <输出路径>")
        sys.exit(1)
    try:
        export_data("测试数据", sys.argv[1])
        print(f"导出成功，文件路径: {sys.argv[1]}")
    except Exception as e:
        print(f"导出失败: {str(e)}")
        sys.exit(2)