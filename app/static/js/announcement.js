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
document.addEventListener('DOMContentLoaded', function() {
    const createBtn = document.getElementById('create-announcement-btn');
    if (createBtn) createBtn.addEventListener('click', createAnnouncement);

    const fetchBtn = document.getElementById('fetch-announcements-btn');
    if (fetchBtn) fetchBtn.addEventListener('click', fetchAnnouncements);
});

// helper to read content from different editors (plain textarea or summernote)
function readAnnouncementContent() {
    // admin editor uses id 'content' (might be a textarea or summernote)
    const contentEl = document.getElementById('content');
    if (contentEl) {
        // if summernote is available (jQuery plugin), prefer its API
        try {
            if (window.jQuery && window.jQuery.fn && window.jQuery.fn.summernote && window.jQuery('#content').summernote) {
                return window.jQuery('#content').summernote('code');
            }
        } catch (e) {
            // ignore and fallback
        }
        return contentEl.value;
    }
    // public simple page uses id 'announcement-content'
    const publicContentEl = document.getElementById('announcement-content');
    if (publicContentEl) return publicContentEl.value;
    return '';
}

// modify createAnnouncement to use readAnnouncementContent and be defensive
function createAnnouncement() {
    const titleEl = document.getElementById('announcement-title') || document.getElementById('title');
    const title = titleEl ? titleEl.value : '';
    const content = readAnnouncementContent();
    const validUntilEl = document.getElementById('announcement-valid-until') || document.getElementById('valid_until');
    const validUntil = validUntilEl ? validUntilEl.value : '';

    if (!title || !content) {
        alert('标题和内容不能为空');
        return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('content', content);
    formData.append('valid_until', validUntil);

    const fileInput = document.getElementById('announcement-attachments') || document.getElementById('announcement-attachment');
    if (fileInput) {
        for (const file of fileInput.files) {
            formData.append('attachments', file);
        }
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
