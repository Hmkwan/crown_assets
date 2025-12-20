"""
公告附件功能测试指南
================================================================================

环境准备:
---------
✓ Docker 容器已启动
✓ 数据库表 announcement_attachment 已创建
✓ 上传目录已创建: app/uploads/announcements, app/uploads/thumbnails

测试步骤:
=========

步骤1: 测试文件上传
-------------------
1. 使用管理员账号登录 (admin)
2. 进入 系统管理 -> 公告管理
3. 点击"新建公告"或编辑已有公告
4. 滚动到页面底部,找到"附件管理"区域
5. 测试以下上传方式:
   □ 拖拽文件到上传区域
   □ 点击上传区域选择文件
6. 测试不同文件类型:
   □ PDF文件 (.pdf)
   □ Word文档 (.doc, .docx)
   □ Excel表格 (.xls, .xlsx)
   □ 图片文件 (.jpg, .png, .gif)
   □ 视频文件 (.mp4)
   
预期结果:
- 上传成功后显示绿色进度条
- 文件出现在附件列表中
- 图片文件自动显示缩略图
- 其他文件显示对应的图标

步骤2: 测试附件管理
-------------------
在编辑页面的附件列表中测试:

1. 查看附件信息:
   □ 文件名是否正确
   □ 文件大小是否显示(如 1.5 MB)
   □ 上传时间是否显示

2. 预览功能(点击"预览"按钮):
   □ PDF文件在弹窗中显示
   □ 图片文件在弹窗中显示
   □ 视频文件可以播放
   
3. 下载功能:
   □ 点击"下载"按钮
   □ 文件下载到本地
   □ 文件名保持原始名称

4. 删除功能:
   □ 点击"删除"按钮
   □ 确认对话框出现
   □ 确认后附件从列表中消失
   □ 刷新页面,附件仍然不显示(软删除生效)

步骤3: 测试用户查看
-------------------
1. 使用普通用户账号登录(如 朱绪)
2. 进入公告列表页面
3. 点击包含附件的公告
4. 在公告详情页底部查看:
   □ 附件列表是否显示
   □ 文件图标是否正确
   □ 文件信息是否完整

5. 测试预览:
   □ 点击"预览"按钮
   □ PDF/图片/视频正常显示
   □ 模态框可以正常关闭

6. 测试下载:
   □ 点击"下载"按钮
   □ 文件正常下载

步骤4: 测试权限控制
-------------------
1. 使用普通用户登录
2. 尝试访问上传API:
   curl -X POST http://localhost:5000/api/announcements/1/upload
   
预期结果:
   □ 返回403权限错误
   □ 普通用户无法看到上传界面

步骤5: 测试边界情况
-------------------
1. 上传超大文件(>50MB):
   □ 应该显示错误提示
   □ 文件不会被保存

2. 上传不支持的文件类型(.exe, .bat):
   □ Dropzone 拒绝文件
   □ 显示"不支持的文件类型"

3. 并发上传多个文件:
   □ 选择多个文件同时上传
   □ 所有文件都成功上传
   □ 列表正确显示所有附件

4. 中文文件名测试:
   □ 上传文件名包含中文的文件
   □ 下载后文件名保持中文
   □ 预览功能正常

故障排查:
=========

问题1: 上传失败
--------------
检查:
- Docker容器是否运行: docker ps
- 上传目录权限: ls -la app/uploads
- 浏览器控制台错误信息
- 服务器日志: docker logs equipment-management-system

问题2: 预览不显示
----------------
检查:
- 文件路径是否正确
- MIME类型是否识别
- 浏览器是否支持预览(PDF需要PDF.js)
- 网络请求是否成功(F12查看Network)

问题3: 附件列表为空
------------------
检查:
- 数据库表是否创建: SELECT * FROM announcement_attachment;
- API是否返回数据
- JavaScript控制台是否有错误

测试完成标准:
=============

□ 所有文件类型都能成功上传
□ 图片、PDF、视频都能正常预览
□ 文件下载功能正常
□ 附件删除功能正常
□ 缩略图生成正常
□ 权限控制生效
□ 中文文件名正常处理
□ 大文件被拒绝
□ 不支持的文件类型被拒绝

测试通过后,即可进入阶段2: 实时通知系统开发

================================================================================
"""

print(__doc__)

# 测试数据库连接
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app, db
    from app.models import AnnouncementAttachment, Announcement
    
    app = create_app()
    with app.app_context():
        # 统计
        total_announcements = Announcement.query.count()
        total_attachments = AnnouncementAttachment.query.count()
        
        print("\n当前数据统计:")
        print(f"  - 公告总数: {total_announcements}")
        print(f"  - 附件总数: {total_attachments}")
        
        if total_announcements > 0:
            print(f"\n可用于测试的公告ID:")
            announcements = Announcement.query.limit(5).all()
            for ann in announcements:
                print(f"  - ID {ann.id}: {ann.title}")
        else:
            print("\n⚠ 提示: 数据库中暂无公告,请先创建公告后再测试附件功能")
            
except Exception as e:
    print(f"\n数据库连接测试失败: {e}")
    print("请确保 Docker 容器正在运行")
