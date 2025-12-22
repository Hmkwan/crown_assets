/**
 * 实时通知系统 - Socket.IO客户端
 * 处理WebSocket连接、通知接收和显示
 */

(function() {
    'use strict';
    
    // Socket.IO连接
    let socket = null;
    let reconnectAttempts = 0;
    const MAX_RECONNECT_ATTEMPTS = 5;
    
    // 通知音效
    const notificationSound = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBi2IzfPTgjMGHm7A7+OZURE5dMny021lGgw+k9vw0H0pByd+y/LZizQHHG3A7+WYUg46c8nx01tlGgs/lNvw0H0pByd+y/LYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7
    
    // 初始化
    function init() {
        console.log('初始化实时通知系统...');
        connectSocket();
        setupNotificationPermission();
    }
    
    // 连接Socket.IO
    function connectSocket() {
        if (socket && socket.connected) {
            console.log('Socket已连接,跳过重复连接');
            return;
        }
        
        socket = io({
            transports: ['websocket', 'polling'],
            upgrade: true,
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            reconnectionAttempts: MAX_RECONNECT_ATTEMPTS
        });
        
        // 连接成功
        socket.on('connected', function(data) {
            console.log('✓ 实时通知已连接:', data);
            reconnectAttempts = 0;
            // showToast('实时通知已连接', 'success'); // 静默连接,不显示提示
        });
        
        // 连接断开
        socket.on('disconnect', function() {
            console.log('✗ 实时通知已断开');
            if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                showToast('连接断开,正在重连...', 'warning');
            }
        });
        
        // 重连尝试
        socket.on('reconnect_attempt', function() {
            reconnectAttempts++;
            console.log(`尝试重连 (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`);
        });
        
        // 重连成功
        socket.on('reconnect', function() {
            console.log('✓ 重连成功');
            reconnectAttempts = 0;
            // showToast('重新连接成功', 'success'); // 静默重连,不显示提示
        });
        
        // 接收通知
        socket.on('notification', function(data) {
            console.log('收到通知:', data);
            handleNotification(data);
        });

        // 接收聊天新消息事件, 格式: { message: {...}, conversation_id: 123 }
        socket.on('new_message', function(data) {
            console.log('收到新消息事件:', data);
            try {
                // 刷新会话列表
                if (typeof loadConversations === 'function') { loadConversations(); }
                // 如果当前正在查看该会话, 则刷新消息
                if (window.currentConversation && window.currentConversation.id === data.conversation_id) {
                    if (typeof loadMessages === 'function') { loadMessages(window.currentConversation.id); }
                }

                // 显示桌面/Toast 并播放声音
                showToast((data.message && data.message.content) || '新消息', 'info', '新聊天消息');
                playNotificationSound();
                showDesktopNotification('新聊天消息', (data.message && data.message.content) || '新消息', `/chat?conversation_id=${data.conversation_id}`);
            } catch (e) {
                console.warn('处理 new_message 事件失败', e);
            }
        });
        
        // 用户上线
        socket.on('user_online', function(data) {
            console.log('用户上线:', data);
        });
        
        // 用户下线
        socket.on('user_offline', function(data) {
            console.log('用户下线:', data);
        });
        
        // Pong响应
        socket.on('pong', function(data) {
            console.log('Pong:', data);
        });
        
        // 错误处理
        socket.on('error', function(error) {
            console.error('Socket错误:', error);
        });
        
        // 心跳
        setInterval(function() {
            if (socket && socket.connected) {
                socket.emit('ping');
            }
        }, 30000); // 每30秒一次心跳
    }
    
    // 处理通知
    function handleNotification(data) {
        const { title, message, type, link, timestamp } = data;

        // 如果是聊天消息, 给聊天模块机会更新会话列表和消息
        if (type === 'new_message' && data.data && data.data.conversation_id) {
            // 优先刷新会话列表
            if (typeof loadConversations === 'function') {
                try { loadConversations(); } catch (e) { console.warn('刷新会话列表失败', e); }
            }
            // 如果当前正在查看该会话则刷新消息
            try {
                if (window.currentConversation && window.currentConversation.id === data.data.conversation_id) {
                    if (typeof loadMessages === 'function') { loadMessages(window.currentConversation.id); }
                }
            } catch (e) { console.warn('加载消息失败', e); }

            // 显示 Toast 与 桌面通知并播放声音
            showToast(message, 'info', title);
            playNotificationSound();
            showDesktopNotification(title, message, link);
            return;
        }

        // 通用通知处理
        showToast(message, type || 'info', title);
        // 播放声音
        playNotificationSound();
        // 显示桌面通知
        showDesktopNotification(title, message, link);

        // 如果有链接,可以添加点击事件
        if (link) {
            console.log('通知链接:', link);
        }

        // 更新未读消息数 (导航栏徽章)
        updateUnreadCount();
    }
    
    // 显示Toast通知
    function showToast(message, type, title) {
        // 使用toastr (AdminLTE自带)
        if (typeof toastr !== 'undefined') {
            toastr.options = {
                closeButton: true,
                progressBar: true,
                positionClass: 'toast-top-right',
                timeOut: 5000,
                extendedTimeOut: 2000,
                onclick: null
            };
            
            switch (type) {
                case 'success':
                    toastr.success(message, title);
                    break;
                case 'error':
                case 'danger':
                    toastr.error(message, title);
                    break;
                case 'warning':
                    toastr.warning(message, title);
                    break;
                default:
                    toastr.info(message, title);
            }
        } else {
            // 后备方案
            alert((title ? title + ': ' : '') + message);
        }
    }
    
    // 播放通知音效
    function playNotificationSound() {
        try {
            notificationSound.play().catch(function(error) {
                console.log('无法播放声音:', error);
            });
        } catch (error) {
            console.log('播放声音异常:', error);
        }
    }
    
    // 请求桌面通知权限
    function setupNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission().then(function(permission) {
                console.log('桌面通知权限:', permission);
            });
        }
    }
    
    // 显示桌面通知
    function showDesktopNotification(title, message, link) {
        if ('Notification' in window && Notification.permission === 'granted') {
            const notification = new Notification(title || '新通知', {
                body: message,
                icon: '/static/dist/img/AdminLTELogo.png',
                badge: '/static/dist/img/AdminLTELogo.png',
                tag: 'equipment-system',
                requireInteraction: false
            });
            
            notification.onclick = function() {
                window.focus();
                if (link) {
                    window.location.href = link;
                }
                notification.close();
            };
            
            // 5秒后自动关闭
            setTimeout(function() {
                notification.close();
            }, 5000);
        }
    }
    
    // 更新未读消息数
    function updateUnreadCount() {
        // 这里可以调用API获取未读消息数并更新UI
        // 例如更新导航栏的消息图标
        const badge = document.querySelector('.navbar-badge');
        if (badge) {
            let count = parseInt(badge.textContent) || 0;
            badge.textContent = count + 1;
            badge.style.display = 'inline-block';
        }
    }
    
    // 公开API
    window.RealtimeNotification = {
        socket: function() { return socket; },
        send: function(event, data) {
            if (socket && socket.connected) {
                socket.emit(event, data);
            }
        },
        joinDepartment: function(departmentId) {
            if (socket && socket.connected) {
                socket.emit('join_department', { department_id: departmentId });
            }
        },
        leaveDepartment: function(departmentId) {
            if (socket && socket.connected) {
                socket.emit('leave_department', { department_id: departmentId });
            }
        }
    };
    
    // 页面加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();
