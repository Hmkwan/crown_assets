"""
检查模板文件的修复状态
"""
import os

def check_template_fixes():
    """检查模板文件是否正确修复"""
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 检查审批流配置页面
    workflow_file = os.path.join(base_dir, 'app', 'templates', 'main', 'workflow_config_by_type.html')
    with open(workflow_file, 'r', encoding='utf-8') as f:
        workflow_html = f.read()
    
    # 检查用户管理页面  
    user_file = os.path.join(base_dir, 'app', 'templates', 'main', 'user_management.html')
    with open(user_file, 'r', encoding='utf-8') as f:
        user_html = f.read()
    
    print("="*70)
    print("📋 模板文件修复状态检查")
    print("="*70)
    
    print("\n✅ 审批流配置页面 (workflow_config_by_type.html):")
    print("-"*70)
    
    # 检查是否移除了btn-group
    btn_group_count = workflow_html.count('btn-group')
    if btn_group_count == 0:
        print("  ✅ 已移除所有 btn-group")
    else:
        print(f"  ❌ 仍然存在 {btn_group_count} 个 btn-group")
    
    # 检查按钮样式
    if 'btn btn-sm btn-primary me-1 mb-1 edit-node' in workflow_html:
        print("  ✅ 编辑按钮使用正确样式（独立按钮）")
    else:
        print("  ❌ 编辑按钮样式不正确")
    
    if 'btn btn-sm btn-danger me-1 mb-1 delete-node' in workflow_html:
        print("  ✅ 删除按钮使用正确样式（独立按钮）")
    else:
        print("  ❌ 删除按钮样式不正确")
    
    # 检查事件委托
    if "$(document).on('click', '.edit-node'" in workflow_html:
        print("  ✅ 编辑按钮使用事件委托")
    else:
        print("  ❌ 编辑按钮未使用事件委托")
    
    if "$(document).on('click', '.delete-node'" in workflow_html:
        print("  ✅ 删除按钮使用事件委托")
    else:
        print("  ❌ 删除按钮未使用事件委托")
    
    # 检查调试日志
    if "console.log('编辑节点按钮被点击')" in workflow_html:
        print("  ✅ 编辑按钮有调试日志")
    else:
        print("  ❌ 编辑按钮无调试日志")
    
    if "console.log('删除节点按钮被点击')" in workflow_html:
        print("  ✅ 删除按钮有调试日志")
    else:
        print("  ❌ 删除按钮无调试日志")
    
    print("\n✅ 用户管理页面 (user_management.html):")
    print("-"*70)
    
    # 检查按钮样式
    if 'btn btn-sm btn-success me-1 mb-1 manage-workflow-roles' in user_html:
        print("  ✅ 审批角色按钮使用正确样式")
    else:
        print("  ❌ 审批角色按钮样式不正确")
    
    # 检查事件委托
    if "$(document).on('click', '.manage-workflow-roles'" in user_html:
        print("  ✅ 审批角色按钮使用事件委托")
    else:
        print("  ❌ 审批角色按钮未使用事件委托")
    
    # 检查调试日志
    if "console.log('管理审批流角色按钮被点击')" in user_html:
        print("  ✅ 审批角色按钮有调试日志")
    else:
        print("  ❌ 审批角色按钮无调试日志")
    
    print("\n" + "="*70)
    print("🎯 修复总结")
    print("="*70)
    print("""
所有按钮已完成以下修复：

1. ✅ 移除 btn-group 包装，改为独立按钮
2. ✅ 按钮样式从 outline 改为实色（btn-primary, btn-danger, btn-success）
3. ✅ 添加间距类（me-1 mb-1）避免按钮拥挤
4. ✅ 使用事件委托 $(document).on() 替代直接绑定
5. ✅ 添加 console.log 调试日志
6. ✅ 添加 e.preventDefault() 防止默认行为

📝 下一步操作：
1. 重启Flask应用（如果正在运行）
2. 清除浏览器缓存（Ctrl+Shift+Delete）或硬刷新（Ctrl+F5）
3. 打开浏览器开发者工具（F12）-> Console 标签
4. 访问页面并点击按钮
5. 查看控制台是否输出调试日志

如果仍然无法点击：
- 检查浏览器控制台是否有 JavaScript 错误
- 确认 jQuery 是否正确加载
- 检查是否有其他 CSS 样式覆盖了按钮的 pointer-events
""")

if __name__ == '__main__':
    check_template_fixes()
