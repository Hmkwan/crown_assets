// 在线用户管理
function fetchOnlineUsers() {
    fetch('/api/online_users')
        .then(response => response.json())
        .then(data => {
            const userList = document.getElementById('online-users-list');
            userList.innerHTML = '';
            data.online_users.forEach(user => {
                const userItem = document.createElement('li');
                userItem.textContent = `用户ID: ${user}`;
                userItem.dataset.userId = user;
                userItem.classList.add('online-user-item');
                userList.appendChild(userItem);
            });
        })
        .catch(error => console.error('获取在线用户失败:', error));
}

function createConversation() {
    const selectedUsers = Array.from(document.querySelectorAll('.online-user-item.selected'))
        .map(item => item.dataset.userId);

    if (selectedUsers.length === 0) {
        alert('请选择至少一个用户创建会话');
        return;
    }

    fetch('/api/create_conversation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            participant_ids: selectedUsers,
            type: selectedUsers.length > 1 ? 'group' : 'direct'
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(`创建会话失败: ${data.error}`);
            } else {
                alert('会话创建成功!');
                console.log('新会话:', data.conversation);
            }
        })
        .catch(error => console.error('创建会话失败:', error));
}

// 事件绑定
document.getElementById('fetch-online-users-btn').addEventListener('click', fetchOnlineUsers);
document.getElementById('create-conversation-btn').addEventListener('click', createConversation);