// 公告管理
function createAnnouncement() {
    const title = document.getElementById('announcement-title').value;
    const content = document.getElementById('announcement-content').value;
    const validUntil = document.getElementById('announcement-valid-until').value;

    if (!title || !content) {
        alert('标题和内容不能为空');
        return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('content', content);
    formData.append('valid_until', validUntil);

    const fileInput = document.getElementById('announcement-attachments');
    for (const file of fileInput.files) {
        formData.append('attachments', file);
    }

    fetch('/api/create_announcement', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(`创建公告失败: ${data.error}`);
            } else {
                alert('公告创建成功!');
                window.location.reload();
            }
        })
        .catch(error => console.error('创建公告失败:', error));
}

function fetchAnnouncements() {
    fetch('/api/get_announcements')
        .then(response => response.json())
        .then(data => {
            const announcementList = document.getElementById('announcement-list');
            announcementList.innerHTML = '';
            data.announcements.forEach(announcement => {
                const item = document.createElement('li');
                item.textContent = `${announcement.title} - ${announcement.content}`;
                announcementList.appendChild(item);
            });
        })
        .catch(error => console.error('获取公告失败:', error));
}

// 事件绑定
document.getElementById('create-announcement-btn').addEventListener('click', createAnnouncement);
document.getElementById('fetch-announcements-btn').addEventListener('click', fetchAnnouncements);