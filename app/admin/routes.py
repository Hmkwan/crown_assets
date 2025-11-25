@admin_bp.route('/users/export')
def export_users():
    try:
        # 业务逻辑：获取用户数据（假设包含中文）
        user_data = "姓名,部门\n张三,技术部\n李四,财务部"
        
        # 统一使用工具函数处理编码和文件写入
        data_bytes = export_data(user_data)
        
        # 响应头必须包含UTF-8声明
        response = make_response(data_bytes)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        from app.utils.import_export import content_disposition
        response.headers['Content-Disposition'] = content_disposition('用户列表.csv', 'users.csv')
        
        return response
    except Exception as e:
        current_app.logger.error(f"用户导出失败: {str(e)}", exc_info=True)
        abort(500, description=f"导出失败: {str(e)}")