// 在线用户管理
function fetchOnlineUsers() {
    fetch('/api/online_users')
        .then(response => response.json())
        .then(data => {
            const userList = document.getElementById('online-users-list');
            userList.innerHTML = '';
            data.online_users.forEach(user => {
                const userItem = document.createElement('li');
                let displayName = '';
                // 支持后端返回字符串ID或对象 {id, username, real_name}
                if (typeof user === 'object') {
                    displayName = user.real_name ? `${user.real_name} (${user.username})` : user.username;
                    userItem.dataset.userId = user.id;
                } else {
                    displayName = `用户ID: ${user}`;
                    userItem.dataset.userId = user;
                }
                userItem.textContent = displayName;
                userItem.classList.add('online-user-item');
                userItem.tabIndex = 0; // 可聚焦
                userList.appendChild(userItem);

                // 点击/回车选择
                userItem.addEventListener('click', () => userItem.classList.toggle('selected'));
                userItem.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') userItem.classList.toggle('selected');
                });
            });
        })
        .catch(error => console.error('获取在线用户失败:', error));
}

// 事件绑定
document.getElementById('fetch-online-users-btn').addEventListener('click', fetchOnlineUsers);
document.getElementById('create-conversation-btn').addEventListener('click', createConversation);

// 支持键盘创建会话（回车）
document.getElementById('create-conversation-btn').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') createConversation();
});

function createConversation() {
    const selectedUsers = Array.from(document.querySelectorAll('.online-user-item.selected'))
        .map(item => item.dataset.userId);

    if (selectedUsers.length === 0) {
        alert('请选择至少一个用户创建会话');
        return;
    }

    const payload = {
        participant_ids: selectedUsers.map(id => parseInt(id, 10)),
        type: selectedUsers.length > 1 ? 'group' : 'direct'
    };
    console.debug('[OnlineUsers] createConversation payload:', payload);
    console.debug('[OnlineUsers] document.cookie:', document.cookie);

    fetch('/api/chat/conversations', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
        .then(response => {
            console.debug('[OnlineUsers] POST /api/chat/conversations status:', response.status, response.statusText, response.headers.get('content-type'));
            if (!response.ok) {
                return response.text().then(text => {
                    try {
                        const j = JSON.parse(text);
                        throw new Error(j.error || j.message || `HTTP ${response.status}`);
                    } catch(e) {
                        console.error('[OnlineUsers] non-JSON error response:', text);
                        throw new Error(text || `HTTP ${response.status}`);
                    }
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('新会话:', data.conversation, 'meta:', {existed: data.existed, joined: data.joined, rejoined: data.rejoined});

            // 如果服务器表示会话已存在但未返回 joined/rejoined，优先尝试通过 GET 获取会话详情（后端会在 direct 场景下自动加入）
            const convObj = data.conversation;
            const attemptSelectFlow = (convId) => {
                // 复用原来的选中/重试逻辑（精简版）
                if (!convId) return;
                let attempts = 0;
                const maxAttempts = 50;
                const trySelect = () => {
                    attempts += 1;
                    if (window.chatSystem && typeof window.chatSystem.selectConversation === 'function') {
                        try {
                            const res = window.chatSystem.selectConversation(convId);
                            if (res && typeof res.then === 'function') {
                                res.then(() => { clearInterval(selTimer); window.removeEventListener('chatSystemReady', onChatReady); }).catch(e => console.warn('[OnlineUsers] selectConversation promise rejected', e));
                                return;
                            } else {
                                clearInterval(selTimer); window.removeEventListener('chatSystemReady', onChatReady); return;
                            }
                        } catch (e) { console.warn('[OnlineUsers] selectConversation threw', e); }
                    }

                    if (typeof loadConversations === 'function') {
                        try { loadConversations(); } catch (e) { console.warn('[OnlineUsers] loadConversations failed', e); }
                    }
                    if (typeof selectConversation === 'function') {
                        try {
                            setTimeout(() => { try { selectConversation(convId); clearInterval(selTimer); window.removeEventListener('chatSystemReady', onChatReady); } catch (e) { console.warn('[OnlineUsers] legacy select threw', e); } }, 400);
                            return;
                        } catch (e) { console.warn('[OnlineUsers] legacy select failed', e); }
                    }

                    if (attempts >= maxAttempts) { clearInterval(selTimer); window.removeEventListener('chatSystemReady', onChatReady); alert('会话已创建，但无法自动选中，请手动刷新会话列表。'); }
                };
                const selTimer = setInterval(trySelect, 200);
                const onChatReady = () => { trySelect(); };
                window.addEventListener('chatSystemReady', onChatReady);
                trySelect();
            };

            // Helper to inject conversation into chatSystem display
            const optimisticPush = (c) => {
                try {
                    if (c && window.chatSystem && Array.isArray(window.chatSystem.conversations)) {
                        if (!window.chatSystem.conversations.find(x => x.id === c.id)) {
                            window.chatSystem.conversations.unshift(c);
                            try { window.chatSystem.renderConversations(); } catch(e) { console.warn('renderConversations failed after optimistic push', e); }
                        }
                    }
                } catch (e) { console.warn('optimistic update failed', e); }
            };

            // Case: existed but server did NOT join/rejoin -> attempt GET first
            if (data.existed && !data.joined && !data.rejoined) {
                if (convObj && convObj.id) {
                    fetch(`/api/chat/conversations/${convObj.id}`, { method: 'GET', credentials: 'same-origin', headers: { 'Content-Type': 'application/json' } })
                        .then(resp => {
                            if (resp.ok) {
                                return resp.json().then(json => {
                                    alert('会话已存在，已恢复或加入会话，正在打开...');
                                    optimisticPush(json.conversation);
                                    attemptSelectFlow(json.conversation.id);
                                }).catch(e => { console.warn('parse conversation json failed', e); if (typeof loadConversations === 'function') try { loadConversations(); } catch(e) {} });
                            } else if (resp.status === 403) {
                                alert('会话已存在但你无权限查看（403），已刷新会话列表');
                                if (typeof loadConversations === 'function') try { loadConversations(); } catch(e) { console.warn('loadConversations failed', e); }
                            } else {
                                // 其他错误，回退到刷新会话并重试选择
                                if (typeof loadConversations === 'function') try { loadConversations(); } catch(e) { console.warn('loadConversations failed', e); }
                                attemptSelectFlow(convObj.id);
                            }
                        })
                        .catch(err => { console.warn('fetch conversation detail failed', err); if (typeof loadConversations === 'function') try { loadConversations(); } catch(e) {} attemptSelectFlow(convObj.id); });
                } else {
                    // 没有 conversation id，则回退到刷新列表
                    if (typeof loadConversations === 'function') try { loadConversations(); } catch(e) { console.warn('loadConversations failed', e); }
                }
                return;
            }

            // 非受限情况（新会话或已 join/rejoined）—原有乐观流程
            alert('会话创建成功!');
            if (convObj) optimisticPush(convObj);
            if (convObj) attemptSelectFlow(convObj.id);
        })
        .catch(error => alert('创建会话失败: ' + (error.message || error)));

}

// 事件绑定
document.getElementById('fetch-online-users-btn').addEventListener('click', fetchOnlineUsers);
document.getElementById('create-conversation-btn').addEventListener('click', createConversation);