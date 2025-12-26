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
        // 检查并显示 toolbar 图标的回退文字（当 font-awesome 被阻止或未加载时）
        this.updateToolbarIconFallbacks();
        // 自动加载在线用户面板内容以提升可用性
        this.fetchOnlineUsers();

        // 回放任何在 chatSystem 就绪前排队的 legacy 调用
        try {
            this.flushLegacyQueue();
        } catch (e) { console.warn('flushLegacyQueue invocation failed', e); }
    }
    
    initSocket() {
        // 优先使用全局 socket，若不可用则尝试 RealtimeNotification 的 socket() 接口
        if (window.socket) {
            this.socket = window.socket;
        } else if (window.RealtimeNotification && typeof window.RealtimeNotification.socket === 'function' && window.RealtimeNotification.socket()) {
            this.socket = window.RealtimeNotification.socket();
        } else {
            console.error('Socket.IO未初始化');
            return;
        }
        // 额外的 socket 生命周期事件，用于诊断与重连处理
        try {
            this.socket.on('connect', () => {
                try { console.debug('[Chat] socket connected, id=', this.socket.id); } catch(e) { console.debug('[Chat] socket connected'); }
                if (this.currentConversation && this.currentConversation.id) {
                    try { this.socket.emit('join_conversation', { conversation_id: this.currentConversation.id }); } catch (e) { console.warn('rejoin conversation after socket connect failed', e); }
                }
            });
            this.socket.on('connect_error', (err) => { console.warn('[Chat] socket connect_error', err); });
            this.socket.on('disconnect', (reason) => { console.warn('[Chat] socket disconnected:', reason); });
            this.socket.on('reconnect_attempt', () => { console.debug('[Chat] socket reconnect attempt'); });
            this.socket.on('reconnect_failed', () => { console.warn('[Chat] socket reconnect_failed'); });
        } catch (e) { console.warn('[Chat] binding socket lifecycle events failed', e); }
        this.registerChatEvents();
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
        const newChatBtn = document.getElementById('newChatBtn');
        const conversationSearch = document.getElementById('conversationSearch');
        const sendBtn = document.getElementById('sendBtn');
        const chatInput = document.getElementById('chatInput');
        const fileUploadBtn = document.getElementById('fileUploadBtn');
        const fileInput = document.getElementById('fileInput');
        const fetchOnlineUsersBtn = document.getElementById('fetch-online-users-btn');
        const createConversationBtn = document.getElementById('create-conversation-btn');
        const emojiBtn = document.getElementById('emojiBtn');
        const showInfoBtn = document.getElementById('showInfoBtn');
        const toggleOnlineUsersBtn = document.getElementById('toggleOnlineUsersBtn');
        const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
        const endConversationBtn = document.getElementById('endConversationBtn');

        // 新建会话按钮
        newChatBtn?.addEventListener('click', () => this.showNewChatModal());

        // 搜索会话
        conversationSearch?.addEventListener('input', (e) => this.searchConversations(e.target.value));

        // 发送消息
        sendBtn?.addEventListener('click', () => this.sendMessage());

        // 输入框事件
        if (chatInput) {
            chatInput.addEventListener('input', () => this.handleTyping());
            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        // 文件上传
        fileUploadBtn?.addEventListener('click', () => fileInput?.click());
        fileInput?.addEventListener('change', (e) => this.handleFileUpload(e.target.files));

        // 在线用户相关按钮
        fetchOnlineUsersBtn?.addEventListener('click', () => this.fetchOnlineUsers());
        createConversationBtn?.addEventListener('click', () => this.showNewChatModal());

        // 工具栏按钮
        emojiBtn?.addEventListener('click', () => this.toggleEmojiPicker());
        showInfoBtn?.addEventListener('click', () => this.showConversationInfo());
        toggleOnlineUsersBtn?.addEventListener('click', () => this.toggleOnlineUsers());
        confirmDeleteBtn?.addEventListener('click', () => this.deleteConversation());
        endConversationBtn?.addEventListener('click', () => this.endConversation());
    }
    
    // 检测 icon 字体是否加载，若被阻止则显示文字回退
    updateToolbarIconFallbacks() {
        try {
            document.querySelectorAll('.toolbar-btn').forEach(btn => {
                const icon = btn.querySelector('i');
                const label = btn.querySelector('.btn-label');
                if (!icon) return;
                const rect = icon.getBoundingClientRect ? icon.getBoundingClientRect() : { width: 0, height: 0 };
                if ((rect.width === 0 && rect.height === 0) && label) {
                    label.style.display = 'inline';
                    icon.style.display = 'none';
                } else if (label) {
                    label.style.display = 'none';
                    icon.style.display = '';
                }
            });
        } catch (e) {
            console.warn('更新 toolbar 图标回退失败', e);
        }
    }

    // 将在 chatSystem 准备前排队的 legacy 调用回放执行
    flushLegacyQueue() {
        try {
            if (!window.__chat_legacy_queue || !window.__chat_legacy_queue.length) return;
            console.debug('[Chat] 回放 legacy 调用, count=', window.__chat_legacy_queue.length);
            while (window.__chat_legacy_queue.length) {
                const item = window.__chat_legacy_queue.shift();
                if (!item || !item.fnName) continue;
                console.debug('[Chat] 回放 legacy 调用:', item.fnName, item.args || []);
                const fn = this[item.fnName];
                if (typeof fn === 'function') {
                    try { fn.apply(this, item.args || []); }
                    catch (e) { console.warn('replaying legacy call failed for', item.fnName, e); }
                } else {
                    console.warn('legacy flush: method not found on ChatSystem:', item.fnName);
                }
            }
            // 如果 wrapper 暴露了清理方法，调用它以清除内部定时器
            if (typeof window.__chat_legacy_clearTimer === 'function') {
                try { window.__chat_legacy_clearTimer(); } catch (e) { console.warn('calling __chat_legacy_clearTimer failed', e); }
            }
        } catch (e) {
            console.error('flushLegacyQueue failed', e);
        }
    }
    
    // ==================== 会话管理 ====================
    
    async loadConversations() {
        console.log('[Chat] 开始加载会话列表...');
        try {
            const response = await fetch('/api/chat/conversations', {
                method: 'GET',
                headers: {'Content-Type': 'application/json'},
                credentials: 'include'
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('[Chat] API错误:', response.status, errorText.substring(0, 200));
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            this.conversations = data.conversations || [];
            console.log('[Chat] 会话列表加载成功:', this.conversations);

            this.flushLegacyQueue();
            this.renderConversations();
            if (!this.currentConversation && this.conversations.length > 0) {
                setTimeout(() => this.selectConversation(this.conversations[0].id), 100);
            }
        } catch (error) {
            console.error('[Chat] 加载会话列表失败:', error);
            this.showToast('加载会话列表失败: ' + error.message, 'error');
            this.conversations = [];
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
                 role="listitem" tabindex="0" data-id="${conv.id}"
                 >
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

        // 添加交互支持（点击或回车选择会话），使用实例方法以避免依赖全局 chatSystem
        container.querySelectorAll('.conversation-item').forEach(item => {
            // 点击选择
            item.addEventListener('click', () => {
                const id = item.dataset.id;
                if (id) this.selectConversation(parseInt(id));
            });
            // 回车键也选择
            item.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    const id = item.dataset.id;
                    if (id) this.selectConversation(parseInt(id));
                }
            });
        });
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
            console.debug('[Chat] selectConversation start:', conversationId);

            // 检查 conversationId 是否有效
            if (!conversationId) {
                console.error('[Chat] selectConversation failed: 无效的会话ID');
                this.showToast('无效的会话ID', 'error');
                return;
            }

            // 确保会话数据已加载；若尚未加载则将调用排入 legacy 队列以在就绪后回放
            if (!this.conversations || this.conversations.length === 0) {
                console.warn('[Chat] selectConversation deferred: 会话数据未加载, enqueueing');
                window.__chat_legacy_queue = window.__chat_legacy_queue || [];
                window.__chat_legacy_queue.push({ fnName: 'selectConversation', args: [conversationId] });
                if (typeof window.__chat_legacy_enqueue === 'function') window.__chat_legacy_enqueue();
                return;
            }

            // 获取会话详情（包含凭据与 CSRF 以避免 403）
            const csrfElem = document.querySelector('input[name="csrf_token"]');
            const csrfToken = csrfElem ? csrfElem.value : (function(){
                const name = 'csrf_token=';
                const ca = document.cookie.split(';');
                for (let i = 0; i < ca.length; i++) {
                    const c = ca[i].trim();
                    if (c.indexOf(name) === 0) return c.substring(name.length);
                }
                return '';
            })();

            const response = await fetch(`/api/chat/conversations/${conversationId}`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            });

            if (!response.ok) {
                console.error('[Chat] selectConversation failed: API响应错误', response.status);
                if (response.status === 403) {
                    const respText = await response.text();
                    console.warn('[Chat] selectConversation 403 response:', respText.substring(0,200));
                    this.showToast('无权限查看该会话（403），请确认你是参与者或重新登录', 'error');
                } else {
                    this.showToast('加载会话失败: API错误', 'error');
                }
                return;
            }

            const data = await response.json();
            if (!data.conversation) {
                console.error('[Chat] selectConversation failed: API未返回会话数据');
                this.showToast('加载会话失败: 数据错误', 'error');
                return;
            }

            this.currentConversation = data.conversation;
            console.debug('[Chat] selectConversation loaded conversation:', this.currentConversation && this.currentConversation.id);

            // 加入会话房间（socket 可能未就绪，容错处理）
            try {
                if (this.socket && typeof this.socket.emit === 'function') {
                    this.socket.emit('join_conversation', { conversation_id: conversationId });
                } else {
                    console.warn('[Chat] socket 未就绪，跳过 join_conversation');
                }
            } catch (e) {
                console.warn('join_conversation error', e);
            }

            // 加载消息历史
            await this.loadMessages(conversationId);

            // 标记已读
            this.markAsRead(conversationId);

            // 更新UI
            this.renderConversations();
            this.renderChatHeader();
            console.debug('[Chat] selectConversation success:', conversationId);

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
                <button id="emojiBtn" class="chat-action-btn toolbar-btn" onclick="chatSystemSafeCall('toggleEmojiPicker')" title="表情">
                    <i class="fas fa-smile"></i>
                </button>
                <button id="fileUploadBtn" class="chat-action-btn toolbar-btn" onclick="document.getElementById('fileInput')?.click()" title="上传文件">
                    <i class="fas fa-paperclip"></i>
                </button>
                <button class="chat-action-btn" onclick="chatSystemSafeCall('togglePin')">
                    <i class="fas fa-thumbtack"></i>
                </button>
                <button class="chat-action-btn" onclick="chatSystemSafeCall('toggleMute')">
                    <i class="fas fa-bell-slash"></i>
                </button>
                <button id="toggleOnlineUsersBtn" class="chat-action-btn toolbar-btn" onclick="chatSystemSafeCall('toggleOnlineUsers')" title="在线用户">
                    <i class="fas fa-users"></i>
                </button>
                <button id="showInfoBtn" class="chat-action-btn toolbar-btn" onclick="chatSystemSafeCall('showConversationInfo')" title="会话信息">
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
                contentHtml = `<img src="${attachment.thumbnail_url || attachment.download_url}" class="message-image" alt="图片" onclick="chatSystemSafeCall('previewImage', '${attachment.download_url}')">`;
            }
        } else if (msg.message_type === 'file') {
            const attachment = msg.attachments?.[0];
            if (attachment) {
                contentHtml = `
                    <div class="message-file" onclick="chatSystemSafeCall('downloadFile', ${attachment.id})">
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
                                <button class="message-action" onclick="chatSystemSafeCall('recallMessage', ${msg.id})">
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

        // 优先使用 Socket.IO，如果未连接则回退到 REST API
        if (this.socket && typeof this.socket.emit === 'function' && this.socket.connected) {
            try {
                this.socket.emit('send_message', {
                    conversation_id: this.currentConversation.id,
                    content: content,
                    message_type: 'text'
                });
            } catch (e) {
                console.error('通过 Socket 发送失败，尝试使用 REST:', e);
                await this._sendMessageRest(content);
            }
        } else {
            await this._sendMessageRest(content);
        }
        
        // 清空输入框
        input.value = '';
        
        // 停止输入状态
        this.stopTyping();
    }

    async _sendMessageRest(content) {
        try {
            const resp = await fetch(`/api/chat/conversations/${this.currentConversation.id}/messages`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message_type: 'text', content })
            });
            if (resp.ok) {
                this.showToast('消息已发送（使用备用通道）', 'success');
                // 主动刷新消息
                await this.loadMessages(this.currentConversation.id);
            } else {
                const data = await resp.json().catch(() => ({}));
                this.showToast(data.error || '消息发送失败', 'error');
            }
        } catch (e) {
            console.error('REST 发送消息失败:', e);
            this.showToast('网络错误：发送失败', 'error');
        }
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
            // 上传文件逻辑
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/chat/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
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
        console.debug('[Chat] handleNewConversation payload:', data);
        // 如果 payload 带有会话 id，优先打开该会话
        const id = (data && (data.conversation && data.conversation.id || data.id || data.conversation_id));
        this.loadConversations().then(() => {
            if (id) {
                try { this.selectConversation(id); } catch (e) { console.warn('select after new_conversation failed, enqueueing', e); window.__chat_legacy_queue = window.__chat_legacy_queue || []; window.__chat_legacy_queue.push({ fnName: 'selectConversation', args: [id] }); if (typeof window.__chat_legacy_enqueue === 'function') window.__chat_legacy_enqueue(); }
            }
        }).catch(e => { console.warn('loadConversations failed after new_conversation', e); });
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

    // 切换在线用户面板显示
    toggleOnlineUsers() {
        const pane = document.querySelector('.online-users-container');
        if (!pane) return;
        pane.classList.toggle('hidden');
    }

    // 拉取在线用户并渲染
    async fetchOnlineUsers() {
        try {
            const ul = document.getElementById('online-users-list');
            if (!ul) return;
            // 显示加载指示
            ul.innerHTML = `
                <li class="list-group-item text-center py-4">
                    <div class="spinner-border text-primary" role="status"><span class="sr-only">加载中...</span></div>
                </li>
            `;

            // 首先获取在线用户ID列表
            const response = await fetch('/api/online_users');
            if (!response.ok) {
                ul.innerHTML = '<li class="list-group-item text-muted">无法获取在线用户</li>';
                return;
            }
            const data = await response.json();
            const ids = data.online_users || [];

            if (ids.length === 0) {
                ul.innerHTML = '<li class="list-group-item text-muted">暂无在线用户</li>';
                return;
            }

            // 获取用户详情并按在线顺序渲染
            const usersResp = await fetch('/api/chat/users');
            if (!usersResp.ok) {
                // 回退到只显示ID的模式
                ul.innerHTML = ids.map(id => `<li class="list-group-item">用户ID: ${id}</li>`).join('');
                return;
            }
            const usersData = await usersResp.json();
            const users = usersData.users || [];
            const userMap = {};
            users.forEach(u => { userMap[u.id] = u; });

            ul.innerHTML = ids.map(id => {
                const u = userMap[id];
                if (u) {
                    return `
                        <li class="list-group-item d-flex align-items-center">
                            <div class="avatar-sm me-2" style="width:32px;height:32px;border-radius:50%;background:#409eff;color:#fff;display:inline-flex;align-items:center;justify-content:center;font-weight:600">${this.escapeHtml((u.real_name||u.username||'').charAt(0).toUpperCase())}</div>
                            <div>${this.escapeHtml(u.real_name || u.username)}</div>
                        </li>
                    `;
                }
                return `<li class="list-group-item">用户ID: ${id}</li>`;
            }).join('');
        } catch (error) {
            console.error('获取在线用户失败:', error);
            const ul = document.getElementById('online-users-list');
            if (ul) ul.innerHTML = '<li class="list-group-item text-muted">加载在线用户时出错</li>';
        }
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

        if (!participantSelect) {
            console.error('[Chat] createNewConversation failed: participantSelect element not found');
            this.showToast('无法找到参与者选择器', 'error');
            return;
        }

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
            // 发送创建会话请求（包含凭据与 CSRF）
            const csrfElem = document.querySelector('input[name="csrf_token"]');
            const csrfToken = csrfElem ? csrfElem.value : (function(){
                const name = 'csrf_token=';
                const ca = document.cookie.split(';');
                for (let i = 0; i < ca.length; i++) {
                    const c = ca[i].trim();
                    if (c.indexOf(name) === 0) return c.substring(name.length);
                }
                return '';
            })();

            const response = await fetch('/api/chat/conversations', {
                method: 'POST',
                headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken},
                credentials: 'include',
                body: JSON.stringify({
                    type: conversationType,
                    participant_ids,
                    name: groupName
                })
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('[Chat] createNewConversation failed: API error', response.status, errorText);
                this.showToast('创建会话失败: ' + errorText, 'error');
                return;
            }

            const data = await response.json();
            console.debug('[Chat] createNewConversation success:', data);

            // 刷新会话列表并尝试打开新创建（或已存在）的会话
            try {
                await this.loadConversations();
                const createdId = data.conversation && data.conversation.id;
                if (createdId) {
                    try {
                        await this.selectConversation(createdId);
                    } catch (e) {
                        console.warn('[Chat] select after create failed, enqueueing:', e);
                        window.__chat_legacy_queue = window.__chat_legacy_queue || [];
                        window.__chat_legacy_queue.push({ fnName: 'selectConversation', args: [createdId] });
                        if (typeof window.__chat_legacy_enqueue === 'function') window.__chat_legacy_enqueue();
                    }
                }
            } catch (e) {
                console.warn('[Chat] loadConversations/select after create encountered an error', e);
            }
            // 隐藏新建对话模态框（如果存在）
            try { $('#newChatModal').modal('hide'); } catch(e) {}
            this.showToast('会话创建成功', 'success');
        } catch (error) {
            console.error('[Chat] createNewConversation failed:', error);
            this.showToast('创建会话失败', 'error');
        }
    }
    
    showConversationInfo() {
        if (!this.currentConversation) {
            this.showToast('请先选择会话', 'warning');
            return;
        }
        const body = document.getElementById('conversationInfoBody');
        if (!body) return;
        const conv = this.currentConversation;
        body.innerHTML = `
            <p><strong>会话名：</strong> ${this.escapeHtml(this.getConversationName(conv))}</p>
            <p><strong>类型：</strong> ${this.escapeHtml(conv.type || '')}</p>
            <p><strong>参与者：</strong> ${this.escapeHtml((conv.participant_count||0).toString())}</p>
            <p><strong>最后消息：</strong> ${this.escapeHtml(conv.last_message?.content || '')}</p>
        `;
        // 绑定模态框底部的按钮（footer 中已有按钮）
        document.getElementById('endConversationBtn')?.addEventListener('click', () => {
            $('#conversationInfoModal').modal('hide');
            this.endConversation();
        });
        // 绑定删除按钮（footer 页的删除按钮）
        document.getElementById('confirmDeleteBtn')?.addEventListener('click', () => {
            // confirmDeleteBtn 已绑定于初始化，UI 内部的删除流程会调用 deleteConversation
        });
        $('#conversationInfoModal').modal('show');
    }

    async deleteConversation() {
        if (!this.currentConversation) {
            this.showToast('无效的会话', 'warning');
            return;
        }
        const id = this.currentConversation.id;
        try {
            // 只有管理员可直接删除会话
            if (window.currentUserIsAdmin) {
                const resp = await fetch(`/api/chat/admin/conversations/${id}`, { method: 'DELETE' });
                if (resp.ok) {
                    this.showToast('会话已删除', 'success');
                    $('#confirmDeleteModal').modal('hide');
                    // 重新加载
                    this.currentConversation = null;
                    this.loadConversations();
                    document.getElementById('chatMessages').innerHTML = '<div class="chat-empty"><i class="fas fa-comments"></i><p>选择一个会话开始聊天</p></div>';
                    return;
                } else {
                    const data = await resp.json().catch(() => ({}));
                    this.showToast(data.error || '删除会话失败', 'error');
                    return;
                }
            }

            // 非管理员：提示需要管理员权限
            this.showToast('删除会话需要管理员权限，请联系管理员', 'warning');
            $('#confirmDeleteModal').modal('hide');
        } catch (e) {
            console.error('删除会话失败:', e);
            this.showToast('删除会话失败：网络错误', 'error');
        }
    }

    async endConversation() {
        if (!this.currentConversation) {
            this.showToast('无效的会话', 'warning');
            return;
        }
        const id = this.currentConversation.id;
        try {
            // 尝试调用用户离开会话的 API (如不存在则回退到本地移除)
            const resp = await fetch(`/api/chat/conversations/${id}/leave`, { method: 'POST' });
            if (resp.ok) {
                this.showToast('已离开会话', 'success');
                this.currentConversation = null;
                // 从本地列表移除
                this.conversations = this.conversations.filter(c => c.id !== id);
                this.renderConversations();
                document.getElementById('chatMessages').innerHTML = '<div class="chat-empty"><i class="fas fa-comments"></i><p>选择一个会话开始聊天</p></div>';
                return;
            }
            // 若服务器返回错误则显示信息
            const data = await resp.json().catch(()=>({}));
            this.showToast(data.error || '离开会话失败', 'error');
        } catch (e) {
            console.warn('离开会话 API 不可用或失败，回退到本地移除', e);
            // 回退：本地移除会话，使用户短期内看不到
            this.conversations = this.conversations.filter(c => c.id !== id);
            this.renderConversations();
            document.getElementById('chatMessages').innerHTML = '<div class="chat-empty"><i class="fas fa-comments"></i><p>选择一个会话开始聊天</p></div>';
            this.showToast('已从列表移除（未同步至服务器）', 'warning');
        }
    }

    toggleEmojiPicker() {
        // 简单 emoji 回退实现：弹出小面板插入 emoji
        const existing = document.getElementById('emojiPicker');
        if (existing) { existing.remove(); return; }
        const btn = document.getElementById('emojiBtn');
        if (!btn) return;
        const picker = document.createElement('div');
        picker.id = 'emojiPicker';
        picker.style.position = 'absolute';
        picker.style.zIndex = 9999;
        picker.style.padding = '6px';
        picker.style.background = '#fff';
        picker.style.border = '1px solid #ddd';
        picker.style.boxShadow = '0 4px 12px rgba(0,0,0,0.08)';
        picker.innerHTML = ['😀','😁','😂','😅','😊','😎','😢','👍','🙏'].map(e => `<button class="emoji-btn" style="border:none;background:none;font-size:20px;margin:4px;cursor:pointer">${e}</button>`).join('');
        document.body.appendChild(picker);
        const r = btn.getBoundingClientRect();
        picker.style.left = (r.left) + 'px';
        picker.style.top = (r.bottom + 6) + 'px';
        picker.querySelectorAll('.emoji-btn').forEach(b => b.addEventListener('click', (ev) => {
            const input = document.getElementById('chatInput');
            if (input) {
                const start = input.selectionStart || 0;
                const end = input.selectionEnd || 0;
                const v = input.value;
                input.value = v.substring(0, start) + ev.target.textContent + v.substring(end);
                input.focus();
            }
            picker.remove();
        }));
        // 点击空白处关闭
        setTimeout(() => document.addEventListener('click', function onDocClick(e){ if (!picker.contains(e.target) && e.target !== btn) { picker.remove(); document.removeEventListener('click', onDocClick); } }));
    }
}

// 初始化 legacy 队列（用于兼容在 chatSystem 就绪前被调用的旧 API）
window.__chat_legacy_queue = window.__chat_legacy_queue || [];
window.__chat_legacy_flush_timer = window.__chat_legacy_flush_timer || null;
window.__chat_legacy_clearTimer = function() { if (window.__chat_legacy_flush_timer) { clearInterval(window.__chat_legacy_flush_timer); window.__chat_legacy_flush_timer = null; } };
window.__chat_legacy_enqueue = function() {
    // 启动定时器定期尝试回放，最长尝试 10s
    if (window.__chat_legacy_flush_timer) return;
    window.__chat_legacy_flush_timer = setInterval(() => {
        if (window.chatSystem && typeof window.chatSystem.flushLegacyQueue === 'function') {
            try { window.chatSystem.flushLegacyQueue(); } catch (e) { console.warn('legacy enqueue flush error', e); }
        }
    }, 500);
    setTimeout(() => { if (window.__chat_legacy_flush_timer) { window.__chat_legacy_clearTimer(); } }, 10000);
};

// 全局安全调用 helper：在 chatSystem 可用时直接执行方法，否则入队回放
window.chatSystemSafeCall = function(fnName, ...args) {
    if (window.chatSystem && typeof window.chatSystem[fnName] === 'function') {
        try { return window.chatSystem[fnName].apply(window.chatSystem, args); } catch (e) { console.warn('chatSystemSafeCall error', fnName, e); }
    } else {
        window.__chat_legacy_queue = window.__chat_legacy_queue || [];
        window.__chat_legacy_queue.push({ fnName, args });
        if (typeof window.__chat_legacy_enqueue === 'function') window.__chat_legacy_enqueue();
    }
};

// 初始化聊天系统
// readiness promise helper for other scripts to await chatSystem
// global readiness promise: resolved by initChatSystem; no auto-reject here (callers should use __chat_wait_for_chatSystem(timeout))
window.__chat_system_ready_promise = new Promise((resolve, reject) => {
    // store resolvers so initChatSystem can resolve/reject
    window.__chat_system_ready_resolve = (val) => {
        console.debug('[Chat] __chat_system_ready_promise resolved');
        try { resolve(val); } finally { window.__chat_system_ready_resolve = null; window.__chat_system_ready_reject = null; }
    };
    window.__chat_system_ready_reject = (err) => {
        console.debug('[Chat] __chat_system_ready_promise rejected', err);
        try { reject(err); } finally { window.__chat_system_ready_resolve = null; window.__chat_system_ready_reject = null; }
    };
});

let chatSystem;
function initChatSystem() {
    try {
        chatSystem = new ChatSystem();
        // 将实例暴露给 window，确保兼容旧代码与 legacy 队列
        try { window.chatSystem = chatSystem; } catch(e) { console.warn('assign window.chatSystem failed', e); }
        console.debug('[ChatSystem] initialized');
        try { window.dispatchEvent(new Event('chatSystemReady')); } catch(e) { console.warn('dispatch chatSystemReady failed', e); }

        // 立即回放任何 legacy 队列内容，并清理定时器
        try {
            if (window.chatSystem && typeof window.chatSystem.flushLegacyQueue === 'function') {
                try { window.chatSystem.flushLegacyQueue(); } catch(e) { console.warn('initial flushLegacyQueue failed', e); }
            }
            if (typeof window.__chat_legacy_clearTimer === 'function') {
                try { window.__chat_legacy_clearTimer(); } catch(e) {}
            }
        } catch (e) { console.warn('[Chat] initial legacy flush failed', e); }

        // resolve readiness promise if somebody is waiting
        try {
            if (window.__chat_system_ready_resolve) {
                window.__chat_system_ready_resolve(window.chatSystem);
                window.__chat_system_ready_resolve = null;
                window.__chat_system_ready_reject = null;
            }
        } catch (e) { console.warn('[Chat] resolving __chat_system_ready_promise failed', e); }
    } catch (e) { console.error('[ChatSystem] initialization failed', e); }
}
// 兼容：若脚本在 DOMContentLoaded 之后加载，则直接初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChatSystem);
} else {
    initChatSystem();
}

// convenience helper: await chatSystem readiness with optional timeout
window.__chat_wait_for_chatSystem = function(timeoutMs = 7000) {
    return new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error('timeout waiting for chatSystem')), timeoutMs);
        window.__chat_system_ready_promise.then(r => { clearTimeout(timer); resolve(r); }).catch(err => { clearTimeout(timer); reject(err); });
    });
};

// 调试助手：显示当前 chatSystem / legacy 队列 状态
window.__chat_debug_status = function() {
    console.groupCollapsed('[Chat Debug Status]');
    console.log('chatSystem exists:', !!window.chatSystem);
    if (window.chatSystem) {
        try { console.log('conversations count:', (window.chatSystem.conversations||[]).length); } catch(e) { console.warn('read convs failed', e); }
        try { console.log('currentConversation id:', window.chatSystem.currentConversation && window.chatSystem.currentConversation.id); } catch(e) {}
    }
    console.log('__chat_legacy_queue size:', (window.__chat_legacy_queue && window.__chat_legacy_queue.length) || 0);
    if (window.__chat_legacy_queue && window.__chat_legacy_queue.length) console.log('queue sample:', window.__chat_legacy_queue.slice(0,5));
    console.log('__chat_legacy_flush_timer exists:', !!window.__chat_legacy_flush_timer);
    console.log('__chat_legacy_clearTimer exists:', typeof window.__chat_legacy_clearTimer === 'function');
    console.groupEnd();
};
