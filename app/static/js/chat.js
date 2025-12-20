// 聊天系统前端逻辑
class ChatSystem {
    constructor() {
        this.currentConversation = null;
        this.conversations = [];
        this.socket = null;
        this.typingTimeout = null;
        this.isTyping = false;
        
        this.init();
    }
    
    init() {
        // 初始化Socket.IO连接
        this.initSocket();
        
        // 加载会话列表
        this.loadConversations();
        
        // 绑定事件
        this.bindEvents();
    }
    
    initSocket() {
        // 使用已有的realtime-notifications.js中的socket
        if (window.socket) {
            this.socket = window.socket;
            this.registerChatEvents();
        } else {
            console.error('Socket.IO未初始化');
        }
    }
    
    registerChatEvents() {
        // 新消息
        this.socket.on('new_message', (data) => {
            this.handleNewMessage(data);
        });
        
        // 用户输入状态
        this.socket.on('user_typing', (data) => {
            this.handleUserTyping(data);
        });
        
        // 消息已读
        this.socket.on('messages_read', (data) => {
            this.handleMessagesRead(data);
        });
        
        // 消息已撤回
        this.socket.on('message_recalled', (data) => {
            this.handleMessageRecalled(data);
        });
        
        // 新会话
        this.socket.on('new_conversation', (data) => {
            this.handleNewConversation(data);
        });
    }
    
    bindEvents() {
        // 新建会话按钮
        document.getElementById('newChatBtn')?.addEventListener('click', () => {
            this.showNewChatModal();
        });
        
        // 搜索会话
        document.getElementById('conversationSearch')?.addEventListener('input', (e) => {
            this.searchConversations(e.target.value);
        });
        
        // 发送消息
        document.getElementById('sendBtn')?.addEventListener('click', () => {
            this.sendMessage();
        });
        
        // 输入框事件
        const chatInput = document.getElementById('chatInput');
        if (chatInput) {
            chatInput.addEventListener('input', () => {
                this.handleTyping();
            });
            
            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
        
        // 文件上传
        document.getElementById('fileUploadBtn')?.addEventListener('click', () => {
            document.getElementById('fileInput')?.click();
        });
        
        document.getElementById('fileInput')?.addEventListener('change', (e) => {
            this.handleFileUpload(e.target.files);
        });
    }
    
    // ==================== 会话管理 ====================
    
    async loadConversations() {
        console.log('[Chat] 开始加载会话列表...');
        try {
            // 提取 CSRF 令牌
            const csrfToken = document.querySelector('input[name="csrf_token"]').value;

            const response = await fetch('/api/chat/conversations', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                },
                credentials: 'include' // 确保发送 Cookie
            });

            console.log('[Chat] API响应状态:', response.status, response.statusText);

            // 检查是否需要登录
            if (response.status === 302 || response.redirected) {
                console.warn('[Chat] 需要登录,跳转到登录页');
                window.location.href = '/auth/login';
                return;
            }

            if (!response.ok) {
                const errorText = await response.text();
                console.error('[Chat] API错误:', response.status, errorText.substring(0, 200));
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            this.conversations = data.conversations;
            console.log('[Chat] 会话列表加载成功:', this.conversations);
        } catch (error) {
            console.error('[Chat] 加载会话列表失败:', error);
            this.showToast('加载会话列表失败: ' + error.message, 'error');
            // 显示空状态
            this.conversations = [];
            this.renderConversations();
        }
    }
    
    renderConversations() {
        const container = document.getElementById('conversationItems');
        if (!container) return;
        
        if (this.conversations.length === 0) {
            container.innerHTML = `
                <div class="text-center p-4 text-muted">
                    <i class="fas fa-comments fa-3x mb-3"></i>
                    <p>暂无会话</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.conversations.map(conv => `
            <div class="conversation-item ${conv.is_pinned ? 'pinned' : ''} ${this.currentConversation?.id === conv.id ? 'active' : ''}"
                 data-id="${conv.id}"
                 onclick="chatSystem.selectConversation(${conv.id})">
                <div class="conversation-avatar">
                    ${this.getConversationAvatar(conv)}
                </div>
                <div class="conversation-info">
                    <div class="conversation-title">
                        <span class="conversation-name">${this.escapeHtml(this.getConversationName(conv))}</span>
                        <span class="conversation-time">${this.formatTime(conv.last_message_time)}</span>
                    </div>
                    <div class="conversation-preview">
                        ${this.escapeHtml(conv.last_message?.content || '暂无消息')}
                        ${conv.unread_count > 0 ? `<span class="conversation-badge">${conv.unread_count}</span>` : ''}
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    getConversationName(conv) {
        if (conv.type === 'direct' && conv.other_user) {
            return conv.other_user.real_name || conv.other_user.username;
        }
        return conv.name || '未命名会话';
    }
    
    getConversationAvatar(conv) {
        if (conv.type === 'direct' && conv.other_user) {
            const name = conv.other_user.real_name || conv.other_user.username;
            return name.charAt(0).toUpperCase();
        }
        return conv.name?.charAt(0).toUpperCase() || '群';
    }
    
    async selectConversation(conversationId) {
        try {
            // 获取会话详情
            const response = await fetch(`/api/chat/conversations/${conversationId}`);
            const data = await response.json();
            
            this.currentConversation = data.conversation;
            
            // 加入会话房间
            this.socket.emit('join_conversation', { conversation_id: conversationId });
            
            // 加载消息历史
            await this.loadMessages(conversationId);
            
            // 标记已读
            this.markAsRead(conversationId);
            
            // 更新UI
            this.renderConversations();
            this.renderChatHeader();
            
        } catch (error) {
            console.error('选择会话失败:', error);
            this.showToast('加载会话失败', 'error');
        }
    }
    
    async loadMessages(conversationId, beforeId = null) {
        try {
            let url = `/api/chat/conversations/${conversationId}/messages?per_page=50`;
            if (beforeId) {
                url += `&before_id=${beforeId}`;
            }
            
            const response = await fetch(url);
            const data = await response.json();
            
            this.renderMessages(data.messages);
            
            // 滚动到底部
            this.scrollToBottom();
            
        } catch (error) {
            console.error('加载消息失败:', error);
            this.showToast('加载消息失败', 'error');
        }
    }
    
    renderChatHeader() {
        const header = document.getElementById('chatHeader');
        if (!header || !this.currentConversation) return;
        
        header.innerHTML = `
            <div class="chat-title">
                ${this.escapeHtml(this.getConversationName(this.currentConversation))}
                ${this.currentConversation.type === 'group' ? `<span class="text-muted ml-2">(${this.currentConversation.participant_count}人)</span>` : ''}
            </div>
            <div class="chat-actions">
                <button class="chat-action-btn" onclick="chatSystem.togglePin()">
                    <i class="fas fa-thumbtack"></i>
                </button>
                <button class="chat-action-btn" onclick="chatSystem.toggleMute()">
                    <i class="fas fa-bell-slash"></i>
                </button>
                <button class="chat-action-btn" onclick="chatSystem.showConversationInfo()">
                    <i class="fas fa-info-circle"></i>
                </button>
            </div>
        `;
    }
    
    renderMessages(messages) {
        const container = document.getElementById('chatMessages');
        if (!container) return;
        
        if (messages.length === 0) {
            container.innerHTML = `
                <div class="chat-empty">
                    <i class="fas fa-comment-dots"></i>
                    <p>开始聊天吧</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = messages.map(msg => this.renderMessage(msg)).join('');
    }
    
    renderMessage(msg) {
        const isOwn = msg.sender_id === window.currentUserId;
        const time = this.formatTime(msg.created_date);
        
        let contentHtml = '';
        if (msg.is_recalled) {
            contentHtml = '<div class="message-recalled">[消息已撤回]</div>';
        } else if (msg.message_type === 'text') {
            contentHtml = `<div class="message-text">${this.escapeHtml(msg.content)}</div>`;
        } else if (msg.message_type === 'image') {
            const attachment = msg.attachments?.[0];
            if (attachment) {
                contentHtml = `<img src="${attachment.thumbnail_url || attachment.download_url}" class="message-image" alt="图片" onclick="chatSystem.previewImage('${attachment.download_url}')">`;
            }
        } else if (msg.message_type === 'file') {
            const attachment = msg.attachments?.[0];
            if (attachment) {
                contentHtml = `
                    <div class="message-file" onclick="chatSystem.downloadFile(${attachment.id})">
                        <i class="fas fa-file message-file-icon"></i>
                        <div class="message-file-info">
                            <div class="message-file-name">${this.escapeHtml(attachment.filename)}</div>
                            <div class="message-file-size">${this.formatFileSize(attachment.file_size)}</div>
                        </div>
                    </div>
                `;
            }
        }
        
        return `
            <div class="message-item ${isOwn ? 'own' : ''}" data-id="${msg.id}">
                <div class="message-avatar">
                    ${(msg.sender_real_name || msg.sender_name).charAt(0).toUpperCase()}
                </div>
                <div class="message-content">
                    ${!isOwn ? `<div class="message-sender">${this.escapeHtml(msg.sender_real_name || msg.sender_name)}</div>` : ''}
                    <div class="message-bubble">
                        ${contentHtml}
                        ${isOwn && !msg.is_recalled ? `
                            <div class="message-actions">
                                <button class="message-action" onclick="chatSystem.recallMessage(${msg.id})">
                                    <i class="fas fa-undo"></i> 撤回
                                </button>
                            </div>
                        ` : ''}
                    </div>
                    <div class="message-time">${time}</div>
                </div>
            </div>
        `;
    }
    
    // ==================== 消息发送 ====================
    
    async sendMessage() {
        if (!this.currentConversation) {
            this.showToast('请先选择会话', 'warning');
            return;
        }
        
        const input = document.getElementById('chatInput');
        const content = input.value.trim();
        
        if (!content) return;
        
        // 通过Socket.IO发送消息
        this.socket.emit('send_message', {
            conversation_id: this.currentConversation.id,
            content: content,
            message_type: 'text'
        });
        
        // 清空输入框
        input.value = '';
        
        // 停止输入状态
        this.stopTyping();
    }
    
    handleTyping() {
        if (!this.currentConversation) return;
        
        // 发送正在输入状态
        if (!this.isTyping) {
            this.socket.emit('typing', {
                conversation_id: this.currentConversation.id,
                is_typing: true
            });
            this.isTyping = true;
        }
        
        // 清除之前的定时器
        if (this.typingTimeout) {
            clearTimeout(this.typingTimeout);
        }
        
        // 3秒后自动停止输入状态
        this.typingTimeout = setTimeout(() => {
            this.stopTyping();
        }, 3000);
    }
    
    stopTyping() {
        if (this.isTyping && this.currentConversation) {
            this.socket.emit('typing', {
                conversation_id: this.currentConversation.id,
                is_typing: false
            });
            this.isTyping = false;
        }
    }
    
    // ==================== 文件上传 ====================
    
    async handleFileUpload(files) {
        if (!files || files.length === 0) return;
        if (!this.currentConversation) {
            this.showToast('请先选择会话', 'warning');
            return;
        }
        
        const file = files[0];
        
        // 检查文件大小(限制20MB)
        if (file.size > 20 * 1024 * 1024) {
            this.showToast('文件大小不能超过20MB', 'error');
            return;
        }
        
        try {
            // 上传文件
            const formData = new FormData();
            formData.append('file', file);
            formData.append('conversation_id', this.currentConversation.id);
            
            const response = await fetch('/api/chat/attachments', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // 判断文件类型
                const messageType = file.type.startsWith('image/') ? 'image' : 'file';
                
                // 发送消息
                this.socket.emit('send_message', {
                    conversation_id: this.currentConversation.id,
                    content: file.name,
                    message_type: messageType,
                    attachment_id: data.attachment_id
                });
                
                this.showToast('文件上传成功', 'success');
            } else {
                this.showToast(data.error || '文件上传失败', 'error');
            }
        } catch (error) {
            console.error('文件上传失败:', error);
            this.showToast('文件上传失败', 'error');
        }
    }
    
    // ==================== Socket事件处理 ====================
    
    handleNewMessage(data) {
        // 添加新消息到列表
        const container = document.getElementById('chatMessages');
        if (container && data.conversation_id === this.currentConversation?.id) {
            // 移除空状态
            if (container.querySelector('.chat-empty')) {
                container.innerHTML = '';
            }
            
            container.insertAdjacentHTML('beforeend', this.renderMessage(data));
            this.scrollToBottom();
            
            // 标记已读
            this.markAsRead(data.conversation_id, data.id);
        }
        
        // 更新会话列表
        this.updateConversationInList(data.conversation_id);
    }
    
    handleUserTyping(data) {
        if (data.conversation_id !== this.currentConversation?.id) return;
        
        const indicator = document.getElementById('typingIndicator');
        if (!indicator) return;
        
        if (data.is_typing) {
            indicator.textContent = `${data.username} 正在输入...`;
            indicator.style.display = 'block';
        } else {
            indicator.style.display = 'none';
        }
    }
    
    handleMessagesRead(data) {
        // 可以显示已读回执
        console.log('消息已读:', data);
    }
    
    handleMessageRecalled(data) {
        // 更新被撤回的消息
        const messageEl = document.querySelector(`.message-item[data-id="${data.message_id}"]`);
        if (messageEl) {
            const bubble = messageEl.querySelector('.message-bubble');
            if (bubble) {
                bubble.innerHTML = '<div class="message-recalled">[消息已撤回]</div>';
            }
        }
    }
    
    handleNewConversation(data) {
        // 添加新会话到列表
        this.loadConversations();
        this.showToast('收到新会话', 'info');
    }
    
    // ==================== 辅助功能 ====================
    
    async markAsRead(conversationId, messageId = null) {
        this.socket.emit('mark_read', {
            conversation_id: conversationId,
            message_id: messageId
        });
        
        // 更新本地会话未读数
        const conv = this.conversations.find(c => c.id === conversationId);
        if (conv) {
            conv.unread_count = 0;
            this.renderConversations();
        }
    }
    
    async recallMessage(messageId) {
        if (!confirm('确定要撤回这条消息吗?')) return;
        
        this.socket.emit('recall_message', { message_id: messageId });
    }
    
    async togglePin() {
        if (!this.currentConversation) return;
        
        try {
            const response = await fetch(`/api/chat/conversations/${this.currentConversation.id}/pin`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ is_pinned: !this.currentConversation.is_pinned })
            });
            
            if (response.ok) {
                this.currentConversation.is_pinned = !this.currentConversation.is_pinned;
                this.loadConversations();
                this.showToast(this.currentConversation.is_pinned ? '已置顶' : '已取消置顶', 'success');
            }
        } catch (error) {
            console.error('置顶失败:', error);
        }
    }
    
    async toggleMute() {
        if (!this.currentConversation) return;
        
        try {
            const response = await fetch(`/api/chat/conversations/${this.currentConversation.id}/mute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ is_muted: !this.currentConversation.is_muted })
            });
            
            if (response.ok) {
                this.currentConversation.is_muted = !this.currentConversation.is_muted;
                this.showToast(this.currentConversation.is_muted ? '已静音' : '已取消静音', 'success');
            }
        } catch (error) {
            console.error('静音失败:', error);
        }
    }
    
    scrollToBottom() {
        const container = document.getElementById('chatMessages');
        if (container) {
            setTimeout(() => {
                container.scrollTop = container.scrollHeight;
            }, 100);
        }
    }
    
    updateConversationInList(conversationId) {
        // 重新加载会话列表
        this.loadConversations();
    }
    
    searchConversations(query) {
        const items = document.querySelectorAll('.conversation-item');
        items.forEach(item => {
            const name = item.querySelector('.conversation-name').textContent.toLowerCase();
            if (name.includes(query.toLowerCase())) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }
    
    // ==================== 工具函数 ====================
    
    formatTime(dateStr) {
        if (!dateStr) return '';
        
        const date = new Date(dateStr);
        const now = new Date();
        const diff = now - date;
        
        // 1分钟内
        if (diff < 60000) {
            return '刚刚';
        }
        
        // 1小时内
        if (diff < 3600000) {
            return Math.floor(diff / 60000) + '分钟前';
        }
        
        // 今天
        if (date.toDateString() === now.toDateString()) {
            return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
        }
        
        // 昨天
        const yesterday = new Date(now);
        yesterday.setDate(yesterday.getDate() - 1);
        if (date.toDateString() === yesterday.toDateString()) {
            return '昨天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
        }
        
        // 其他
        return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' });
    }
    
    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB';
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    showToast(message, type = 'info') {
        // 使用现有的Toast通知系统
        if (window.showToast) {
            window.showToast(message, type);
        } else {
            alert(message);
        }
    }
    
    previewImage(url) {
        window.open(url, '_blank');
    }
    
    downloadFile(attachmentId) {
        window.location.href = `/api/chat/attachments/${attachmentId}/download`;
    }
    
    async showNewChatModal() {
        // 加载用户列表
        try {
            const response = await fetch('/api/chat/users');
            
            // 检查是否需要登录
            if (response.status === 302 || response.redirected) {
                window.location.href = '/auth/login';
                return;
            }
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            
            if (!data.users) {
                this.showToast('获取用户列表失败', 'error');
                return;
            }
            
            // 填充用户选择列表
            const participantSelect = document.getElementById('participantSelect');
            if (participantSelect) {
                participantSelect.innerHTML = data.users.map(user => `
                    <option value="${user.id}">
                        ${this.escapeHtml(user.real_name || user.username)} 
                        (${this.escapeHtml(user.department)})
                    </option>
                `).join('');
            }
            
            // 显示模态框
            $('#newChatModal').modal('show');
            
            // 绑定会话类型切换事件
            const conversationType = document.getElementById('conversationType');
            if (conversationType) {
                conversationType.addEventListener('change', (e) => {
                    const groupNameGroup = document.getElementById('groupNameGroup');
                    if (groupNameGroup) {
                        groupNameGroup.style.display = e.target.value === 'group' ? 'block' : 'none';
                    }
                });
            }
            
            // 绑定创建按钮
            const createChatBtn = document.getElementById('createChatBtn');
            if (createChatBtn) {
                createChatBtn.onclick = () => this.createNewConversation();
            }
            
        } catch (error) {
            console.error('加载用户列表失败:', error);
            this.showToast('加载用户列表失败', 'error');
        }
    }
    
    async createNewConversation() {
        const conversationType = document.getElementById('conversationType')?.value || 'direct';
        const groupName = document.getElementById('groupName')?.value;
        const participantSelect = document.getElementById('participantSelect');
        
        if (!participantSelect) return;
        
        // 获取选中的参与者
        const selectedOptions = Array.from(participantSelect.selectedOptions);
        const participant_ids = selectedOptions.map(opt => parseInt(opt.value));
        
        if (participant_ids.length === 0) {
            this.showToast('请选择至少一个参与者', 'warning');
            return;
        }
        
        if (conversationType === 'direct' && participant_ids.length > 1) {
            this.showToast('一对一会话只能选择一个参与者', 'warning');
            return;
        }
        
        if (conversationType === 'group' && !groupName) {
            this.showToast('请输入群组名称', 'warning');
            return;
        }
        
        try {
            const response = await fetch('/api/chat/conversations', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    type: conversationType,
                    participant_ids,
                    name: groupName
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                $('#newChatModal').modal('hide');
                this.showToast('会话创建成功', 'success');
                this.loadConversations();
                
                // 如果返回了会话ID,自动选中
                if (data.conversation && data.conversation.id) {
                    setTimeout(() => {
                        this.selectConversation(data.conversation.id);
                    }, 500);
                }
            } else {
                this.showToast(data.error || '创建会话失败', 'error');
            }
        } catch (error) {
            console.error('创建会话失败:', error);
            this.showToast('创建会话失败', 'error');
        }
    }
    
    showConversationInfo() {
        // TODO: 实现会话信息对话框
        alert('会话信息功能开发中...');
    }
}

// 初始化聊天系统
let chatSystem;
document.addEventListener('DOMContentLoaded', () => {
    chatSystem = new ChatSystem();
});
