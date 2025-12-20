// 聊天管理系统前端逻辑
class ChatAdmin {
    constructor() {
        this.currentPage = {
            conversations: 1,
            messages: 1
        };
        this.charts = {};
        this.init();
    }
    
    init() {
        // 加载统计数据
        this.loadStatistics();
        
        // 加载会话列表
        this.loadConversations();
        
        // 加载活跃用户
        this.loadActiveUsers();
        
        // 绑定事件
        this.bindEvents();
    }
    
    bindEvents() {
        // Tab切换事件
        $('a[data-toggle="tab"]').on('shown.bs.tab', (e) => {
            const target = $(e.target).attr('href');
            if (target === '#messages' && !this.messagesLoaded) {
                this.loadMessages();
                this.messagesLoaded = true;
            }
        });
        
        // 会话类型筛选
        $('#conversationTypeFilter').on('change', () => {
            this.currentPage.conversations = 1;
            this.loadConversations();
        });
        
        // 消息搜索
        $('#searchMessagesBtn').on('click', () => {
            this.currentPage.messages = 1;
            this.loadMessages();
        });
        
        $('#messageSearchInput').on('keypress', (e) => {
            if (e.which === 13) {
                this.currentPage.messages = 1;
                this.loadMessages();
            }
        });
    }
    
    async loadStatistics() {
        console.log('[ChatAdmin] 开始加载统计数据...');
        try {
            const response = await fetch('/api/chat/admin/statistics', {
                credentials: 'same-origin'  // 确保发送cookie
            });
            console.log('[ChatAdmin] 统计API响应:', response.status, response.statusText, response.url);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('[ChatAdmin] 统计API错误:', errorText.substring(0, 500));
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            console.log('[ChatAdmin] 统计数据:', data);
            
            // 更新统计卡片
            $('#totalConversations').text(data.total_conversations || 0);
            $('#totalMessages').text(data.total_messages || 0);
            $('#activeUsers').text(data.active_users || 0);
            $('#totalAttachments').text(data.total_attachments || 0);
            
            // 渲染图表
            if (data.message_trend && data.message_trend.length > 0) {
                this.renderMessageTrendChart(data.message_trend);
            } else {
                console.warn('[ChatAdmin] 消息趋势数据为空');
            }
            
            if (data.conversation_types) {
                this.renderConversationTypeChart(data.conversation_types);
            } else {
                console.warn('[ChatAdmin] 会话类型数据为空');
            }
        } catch (error) {
            console.error('[ChatAdmin] 加载统计数据失败:', error);
            this.showToast('加载统计数据失败: ' + error.message, 'error');
        }
    }
    
    renderMessageTrendChart(data) {
        const ctx = document.getElementById('messageTrendChart');
        if (!ctx) return;
        
        if (this.charts.messageTrend) {
            this.charts.messageTrend.destroy();
        }
        
        this.charts.messageTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d.date),
                datasets: [{
                    label: '消息数量',
                    data: data.map(d => d.count),
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }
    
    renderConversationTypeChart(data) {
        const ctx = document.getElementById('conversationTypeChart');
        if (!ctx) return;
        
        if (this.charts.conversationType) {
            this.charts.conversationType.destroy();
        }
        
        const labels = {
            'direct': '一对一',
            'group': '群组'
        };
        
        this.charts.conversationType = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(data).map(k => labels[k] || k),
                datasets: [{
                    data: Object.values(data),
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 99, 132, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    async loadConversations(page = 1) {
        try {
            const type = $('#conversationTypeFilter').val();
            const params = new URLSearchParams({
                page: page,
                per_page: 20
            });
            
            if (type) params.append('type', type);
            
            const response = await fetch(`/api/chat/admin/conversations?${params}`, {
                credentials: 'same-origin'
            });
            const data = await response.json();
            console.log('[ChatAdmin] 会话列表API响应:', response.status, data);
            
            if (response.ok) {
                this.renderConversations(data.conversations);
                this.renderPagination('conversations', data.current_page, data.pages);
            } else {
                this.showToast('加载会话列表失败', 'error');
            }
        } catch (error) {
            console.error('加载会话列表失败:', error);
            this.showToast('加载会话列表失败', 'error');
        }
    }
    
    renderConversations(conversations) {
        const tbody = $('#conversationsTableBody');
        
        if (conversations.length === 0) {
            tbody.html(`
                <tr>
                    <td colspan="8" class="text-center text-muted">
                        <div class="empty-state">
                            <i class="fas fa-inbox"></i>
                            <p>暂无会话</p>
                        </div>
                    </td>
                </tr>
            `);
            return;
        }
        
        const typeLabels = {
            'direct': '<span class="badge badge-direct">一对一</span>',
            'group': '<span class="badge badge-group">群组</span>'
        };
        
        tbody.html(conversations.map(conv => `
            <tr class="fade-in">
                <td>${conv.id}</td>
                <td>${typeLabels[conv.conversation_type] || conv.conversation_type}</td>
                <td>${this.escapeHtml(conv.name || '未命名')}</td>
                <td><span class="badge badge-info">${conv.participant_count}</span></td>
                <td><span class="badge badge-primary">${conv.message_count}</span></td>
                <td>${this.formatTime(conv.last_message_time)}</td>
                <td>${this.formatTime(conv.created_date)}</td>
                <td>
                    <button class="btn btn-sm btn-action btn-view" onclick="chatAdmin.viewConversation(${conv.id})">
                        <i class="fas fa-eye"></i> 查看
                    </button>
                    <button class="btn btn-sm btn-action btn-delete" onclick="chatAdmin.deleteConversation(${conv.id})">
                        <i class="fas fa-trash"></i> 删除
                    </button>
                </td>
            </tr>
        `).join(''));
    }
    
    async loadMessages(page = 1) {
        try {
            const keyword = $('#messageSearchInput').val();
            const params = new URLSearchParams({
                page: page,
                per_page: 50
            });
            
            if (keyword) params.append('keyword', keyword);
            
            const response = await fetch(`/api/chat/admin/messages?${params}`, {
                credentials: 'same-origin'
            });
            const data = await response.json();
            
            if (response.ok) {
                this.renderMessages(data.messages);
                this.renderPagination('messages', data.current_page, data.pages);
            } else {
                this.showToast('加载消息列表失败', 'error');
            }
        } catch (error) {
            console.error('加载消息列表失败:', error);
            this.showToast('加载消息列表失败', 'error');
        }
    }
    
    renderMessages(messages) {
        const tbody = $('#messagesTableBody');
        
        if (messages.length === 0) {
            tbody.html(`
                <tr>
                    <td colspan="6" class="text-center text-muted">
                        <div class="empty-state">
                            <i class="fas fa-search"></i>
                            <p>没有找到消息</p>
                        </div>
                    </td>
                </tr>
            `);
            return;
        }
        
        const typeLabels = {
            'text': '<span class="badge badge-secondary">文本</span>',
            'image': '<span class="badge badge-primary">图片</span>',
            'file': '<span class="badge badge-info">文件</span>'
        };
        
        tbody.html(messages.map(msg => `
            <tr class="fade-in">
                <td>${msg.id}</td>
                <td>${this.escapeHtml(msg.sender_name || '未知')}</td>
                <td>
                    <div class="message-content" title="${this.escapeHtml(msg.content || '')}">
                        ${this.escapeHtml(msg.content || '(附件)')}
                    </div>
                </td>
                <td>${typeLabels[msg.message_type] || msg.message_type}</td>
                <td>${this.formatTime(msg.created_date)}</td>
                <td>
                    <button class="btn btn-sm btn-action btn-delete" onclick="chatAdmin.deleteMessage(${msg.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join(''));
    }
    
    async loadActiveUsers() {
        try {
            const response = await fetch('/api/chat/admin/users/chat-active', {
                credentials: 'same-origin'
            });
            const data = await response.json();
            console.log('[ChatAdmin] 活跃用户响应:', response.status, data);
            
            if (response.ok) {
                this.renderActiveUsers(data.users);
            } else {
                this.showToast('加载活跃用户失败', 'error');
            }
        } catch (error) {
            console.error('加载活跃用户失败:', error);
            this.showToast('加载活跃用户失败', 'error');
        }
    }
    
    renderActiveUsers(users) {
        const tbody = $('#usersTableBody');
        
        if (users.length === 0) {
            tbody.html(`
                <tr>
                    <td colspan="6" class="text-center text-muted">
                        <div class="empty-state">
                            <i class="fas fa-user-slash"></i>
                            <p>暂无活跃用户</p>
                        </div>
                    </td>
                </tr>
            `);
            return;
        }
        
        tbody.html(users.map((user, index) => `
            <tr class="fade-in">
                <td>
                    ${index < 3 ? `<span class="badge badge-warning">${index + 1}</span>` : index + 1}
                </td>
                <td>${this.escapeHtml(user.username)}</td>
                <td>${this.escapeHtml(user.real_name)}</td>
                <td>${this.escapeHtml(user.department)}</td>
                <td><span class="badge badge-primary">${user.message_count}</span></td>
                <td>${this.formatTime(user.last_message_time)}</td>
            </tr>
        `).join(''));
    }
    
    renderPagination(type, currentPage, totalPages) {
        const container = $(`#${type}Pagination`);
        
        if (totalPages <= 1) {
            container.html('');
            return;
        }
        
        let html = '';
        
        // 上一页
        html += `
            <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="chatAdmin.changePage('${type}', ${currentPage - 1}); return false;">
                    <i class="fas fa-chevron-left"></i>
                </a>
            </li>
        `;
        
        // 页码
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            html += `
                <li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="chatAdmin.changePage('${type}', ${i}); return false;">
                        ${i}
                    </a>
                </li>
            `;
        }
        
        // 下一页
        html += `
            <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="chatAdmin.changePage('${type}', ${currentPage + 1}); return false;">
                    <i class="fas fa-chevron-right"></i>
                </a>
            </li>
        `;
        
        container.html(html);
    }
    
    changePage(type, page) {
        this.currentPage[type] = page;
        if (type === 'conversations') {
            this.loadConversations(page);
        } else if (type === 'messages') {
            this.loadMessages(page);
        }
    }
    
    viewConversation(id) {
        // 跳转到聊天页面并选中该会话
        window.location.href = `/chat?conversation_id=${id}`;
    }
    
    async deleteConversation(id) {
        if (!confirm('确定要删除这个会话吗?这将删除所有相关消息,且不可恢复!')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/chat/admin/conversations/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.showToast('会话已删除', 'success');
                this.loadConversations(this.currentPage.conversations);
                this.loadStatistics(); // 重新加载统计
            } else {
                const data = await response.json();
                this.showToast(data.error || '删除失败', 'error');
            }
        } catch (error) {
            console.error('删除会话失败:', error);
            this.showToast('删除会话失败', 'error');
        }
    }
    
    async deleteMessage(id) {
        if (!confirm('确定要删除这条消息吗?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/chat/admin/messages/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.showToast('消息已删除', 'success');
                this.loadMessages(this.currentPage.messages);
                this.loadStatistics(); // 重新加载统计
            } else {
                const data = await response.json();
                this.showToast(data.error || '删除失败', 'error');
            }
        } catch (error) {
            console.error('删除消息失败:', error);
            this.showToast('删除消息失败', 'error');
        }
    }
    
    formatTime(timeStr) {
        if (!timeStr) return '-';
        const date = new Date(timeStr);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return '刚刚';
        if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前';
        if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前';
        if (diff < 604800000) return Math.floor(diff / 86400000) + '天前';
        
        return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return (text || '').replace(/[&<>"']/g, m => map[m]);
    }
    
    showToast(message, type = 'info') {
        // 使用Bootstrap的Toast或者简单的alert
        // 这里简化处理
        const alertClass = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[type] || 'alert-info';
        
        const toast = $(`
            <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
                 style="top: 20px; right: 20px; z-index: 9999; min-width: 250px;">
                ${message}
                <button type="button" class="close" data-dismiss="alert">
                    <span>&times;</span>
                </button>
            </div>
        `);
        
        $('body').append(toast);
        
        setTimeout(() => {
            toast.alert('close');
        }, 3000);
    }
}

// 初始化
let chatAdmin;
document.addEventListener('DOMContentLoaded', () => {
    console.log('[ChatAdmin] DOM加载完成,开始初始化...');
    chatAdmin = new ChatAdmin();
    console.log('[ChatAdmin] ChatAdmin实例已创建');
});
