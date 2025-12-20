#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
项目完整备份工具
自动备份所有必要的项目文件，方便迁移到其他设备
"""

import os
import shutil
import zipfile
from datetime import datetime
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(BASE_DIR, 'project_backups')

# 需要备份的目录
DIRECTORIES_TO_BACKUP = [
    'app',
    'alembic',
    'migrations',
    'scripts',
    'static',
    'tests',
]

# 需要备份的单个文件
FILES_TO_BACKUP = [
    'app.py',
    'config.py',
    'requirements.txt',
    'alembic.ini',
    'boot.bat',
    'boot.sh',
    'init_db.py',
    'init_default_workflow.py',
    'create_admin.py',
    'check_index.py',
    'download_cdn_resources.py',
    'update_base_template.py',
    # 文档文件
    'QUICK_START_GUIDE.md',
    'DEPLOYMENT_OPTIMIZATION_GUIDE.md',
    'PERFORMANCE_DIAGNOSIS.md',
    'DEVELOPMENT_REPORT.md',
    'DELIVERY_CHECKLIST.md',
    'FINAL_DELIVERY.md',
    'PERMISSION_SYSTEM_ENHANCEMENT.md',
    'REPORTS_FIXES_SUMMARY.md',
    'SYSTEM_IMPROVEMENT_PLAN.md',
    'WORKFLOW_ENHANCEMENTS.md',
]

# 需要备份的数据库文件（可选）
DATABASE_FILES = [
    'app.db',
]

# 排除的文件和目录模式
EXCLUDE_PATTERNS = [
    '__pycache__',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '.pytest_cache',
    '.venv',
    'venv',
    'env',
    '*.log',
    'stdout.txt',
    'stderr.txt',
    '.git',
    '.gitignore',
    'project_backups',
    'backups',
]


def should_exclude(path, exclude_patterns):
    """判断路径是否应该被排除"""
    path_parts = path.split(os.sep)
    for pattern in exclude_patterns:
        if pattern.startswith('*'):
            # 文件扩展名匹配
            if path.endswith(pattern[1:]):
                return True
        else:
            # 目录或文件名匹配
            if pattern in path_parts or os.path.basename(path) == pattern:
                return True
    return False


def get_directory_size(path):
    """计算目录大小"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return total_size


def format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def create_backup(include_database=True):
    """创建项目备份"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"project_backup_{timestamp}"
    temp_backup_dir = os.path.join(BACKUP_DIR, backup_name)
    zip_file_path = os.path.join(BACKUP_DIR, f"{backup_name}.zip")
    
    print("=" * 70)
    print("项目备份工具")
    print("=" * 70)
    print(f"备份时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"项目目录: {BASE_DIR}")
    print(f"备份目录: {BACKUP_DIR}")
    print("=" * 70)
    
    # 创建备份目录
    os.makedirs(temp_backup_dir, exist_ok=True)
    
    backup_info = {
        'backup_time': datetime.now().isoformat(),
        'project_path': BASE_DIR,
        'files': [],
        'directories': [],
        'total_size': 0,
    }
    
    file_count = 0
    total_size = 0
    
    # 备份目录
    print("\n正在备份目录...")
    for dir_name in DIRECTORIES_TO_BACKUP:
        src_dir = os.path.join(BASE_DIR, dir_name)
        if os.path.exists(src_dir):
            dst_dir = os.path.join(temp_backup_dir, dir_name)
            print(f"  ├─ {dir_name}/", end='')
            
            dir_file_count = 0
            # 复制目录，排除不需要的文件
            for root, dirs, files in os.walk(src_dir):
                # 过滤目录
                dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), EXCLUDE_PATTERNS)]
                
                rel_root = os.path.relpath(root, src_dir)
                dst_root = os.path.join(dst_dir, rel_root) if rel_root != '.' else dst_dir
                os.makedirs(dst_root, exist_ok=True)
                
                for file in files:
                    src_file = os.path.join(root, file)
                    if not should_exclude(src_file, EXCLUDE_PATTERNS):
                        dst_file = os.path.join(dst_root, file)
                        shutil.copy2(src_file, dst_file)
                        file_size = os.path.getsize(src_file)
                        total_size += file_size
                        file_count += 1
                        dir_file_count += 1
            
            dir_size = get_directory_size(dst_dir)
            print(f" ({dir_file_count} 个文件, {format_size(dir_size)})")
            backup_info['directories'].append({
                'name': dir_name,
                'size': dir_size,
                'file_count': dir_file_count,
            })
    
    # 备份单个文件
    print("\n正在备份配置文件...")
    for file_name in FILES_TO_BACKUP:
        src_file = os.path.join(BASE_DIR, file_name)
        if os.path.exists(src_file):
            dst_file = os.path.join(temp_backup_dir, file_name)
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            shutil.copy2(src_file, dst_file)
            file_size = os.path.getsize(src_file)
            total_size += file_size
            file_count += 1
            print(f"  ├─ {file_name} ({format_size(file_size)})")
            
            backup_info['files'].append({
                'name': file_name,
                'size': file_size,
            })
    
    # 备份数据库文件（可选）
    if include_database:
        print("\n正在备份数据库文件...")
        for db_file in DATABASE_FILES:
            src_file = os.path.join(BASE_DIR, db_file)
            if os.path.exists(src_file):
                dst_file = os.path.join(temp_backup_dir, db_file)
                shutil.copy2(src_file, dst_file)
                file_size = os.path.getsize(src_file)
                total_size += file_size
                file_count += 1
                print(f"  ├─ {db_file} ({format_size(file_size)})")
                
                backup_info['files'].append({
                    'name': db_file,
                    'size': file_size,
                })
    
    # 创建备份信息文件
    backup_info['total_size'] = total_size
    backup_info['file_count'] = file_count
    
    info_file = os.path.join(temp_backup_dir, 'BACKUP_INFO.json')
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(backup_info, f, indent=2, ensure_ascii=False)
    
    # 创建README文件
    readme_content = f"""# 项目备份

备份时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
原项目路径: {BASE_DIR}

## 备份内容

### 目录 ({len(backup_info['directories'])}个)
{chr(10).join(f"- {d['name']}/ ({d.get('file_count', 0)} 个文件, {format_size(d['size'])})" for d in backup_info['directories'])}

### 文件 ({len(backup_info['files'])}个)
{chr(10).join(f"- {f['name']} ({format_size(f['size'])})" for f in backup_info['files'])}

总计: {file_count} 个文件, {format_size(total_size)}

## 恢复步骤

1. 解压备份文件到目标目录
2. 安装Python 3.7+
3. 创建虚拟环境:
   ```
   python -m venv .venv
   .venv\\Scripts\\activate  (Windows)
   source .venv/bin/activate  (Linux/Mac)
   ```
4. 安装依赖:
   ```
   pip install -r requirements.txt
   ```
5. 初始化数据库（如果没有备份数据库）:
   ```
   python init_db.py
   python create_admin.py
   ```
6. 启动服务:
   ```
   python app.py
   ```

## 注意事项

- 确保Python版本一致
- 检查数据库文件是否完整
- 根据新环境修改config.py中的配置
- 首次运行前清除浏览器缓存

更多信息请查看 QUICK_START_GUIDE.md
"""
    
    readme_file = os.path.join(temp_backup_dir, 'README_RESTORE.md')
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # 压缩备份
    print("\n正在压缩备份文件...")
    compressed_count = 0
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_backup_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_backup_dir)
                zipf.write(file_path, arcname)
                compressed_count += 1
                if compressed_count % 10 == 0:
                    print(f"  已压缩 {compressed_count} 个文件...")
    
    # 删除临时目录
    shutil.rmtree(temp_backup_dir)
    
    zip_size = os.path.getsize(zip_file_path)
    compression_ratio = (1 - zip_size / total_size) * 100 if total_size > 0 else 0
    
    print("\n" + "=" * 70)
    print("备份完成！")
    print("=" * 70)
    print(f"备份文件: {zip_file_path}")
    print(f"文件数量: {file_count} 个")
    print(f"原始大小: {format_size(total_size)}")
    print(f"压缩大小: {format_size(zip_size)}")
    print(f"压缩率: {compression_ratio:.1f}%")
    print("=" * 70)
    print("\n下一步:")
    print(f"1. 将备份文件复制到目标设备: {os.path.basename(zip_file_path)}")
    print("2. 解压备份文件")
    print("3. 按照 README_RESTORE.md 中的步骤恢复项目")
    print("\n备份文件位置:")
    print(f"  {zip_file_path}")
    
    return zip_file_path


def main():
    """主函数"""
    try:
        print("\n是否包含数据库文件备份？")
        print("1. 是（包含app.db，完整备份）")
        print("2. 否（仅备份代码和配置，新设备需重新初始化数据库）")
        
        choice = input("\n请选择 [1/2，默认1]: ").strip() or '1'
        include_db = choice == '1'
        
        if include_db:
            print("\n将备份完整项目（包含数据库）")
        else:
            print("\n将仅备份代码和配置文件")
        
        print("\n开始备份...")
        zip_file = create_backup(include_database=include_db)
        
        print("\n✓ 备份成功！")
        
    except KeyboardInterrupt:
        print("\n\n备份已取消")
    except Exception as e:
        print(f"\n✗ 备份失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
