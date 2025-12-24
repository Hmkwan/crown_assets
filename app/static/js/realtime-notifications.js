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
    const notificationSound = new Audio('data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YQAAAAA=');

    // 初始化lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7+WYUg46c8nw01xlGgs/lNrwz34qBSd9yvLYijUGHGy/7
    
    // 初始化
    function init() {
        console.log('初始化实时通知系统...');

        // 检测 storage 是否可用（某些浏览器隐私设置会阻止第三方或所有站点的 storage）
        if (!storageAvailable('localStorage')) {
            console.warn('localStorage 不可用：某些功能可能受限（跟踪防护已阻止存储）');
            showToast('浏览器阻止了存储访问，某些功能可能受限，请允许站点存储或禁用跟踪防护', 'warning');
            window.__storage_available = false;
        } else {
            window.__storage_available = true;
        }

        // 如果早期检测到 socket 客户端缺失（CDN & 本地脚本均未加载），提示用户
        if (window.__socket_client_missing) {
            console.warn('检测到 socket 客户端未加载: 提示用户检查浏览器策略或站点资源');
            showToast('实时功能客户端未能加载，某些功能可能受限。请允许站点加载外部脚本或禁用跟踪防护', 'warning');
        }

        connectSocket();
        setupNotificationPermission();
    }
    
    // 检查 Storage 可用性
    function storageAvailable(type = 'localStorage') {
        try {
            var storage = window[type];
            var x = '__storage_test__';
            storage.setItem(x, x);
            storage.removeItem(x);
            return true;
        } catch (e) {
            return false;
        }
    }

    // 连接Socket.IO
    function connectSocket() {
        if (socket && socket.connected) {
            console.log('Socket已连接,跳过重复连接');
            return;
        }

        if (typeof io === 'undefined') {
            console.error('Socket.IO 客户端未加载 (io 未定义) —— 可能被跟踪防护或CDN阻止');
            showToast('实时功能未加载：请检查静态资源加载或禁用跟踪防护', 'error');
            return;
        }

        console.log('尝试连接 Socket.IO...');
        // 可选增强：允许通过全局 window.SOCKET_IO_OPTS 覆盖默认的 Socket.IO 连接配置（例如 timeout/回退策略）
        const DEFAULT_SOCKET_OPTS = {
            transports: ['websocket', 'polling'],
            upgrade: true,
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            reconnectionAttempts: MAX_RECONNECT_ATTEMPTS,
            timeout: 20000,
            autoConnect: true
        };
        const userSocketOpts = (typeof window.SOCKET_IO_OPTS === 'object' && window.SOCKET_IO_OPTS) ? window.SOCKET_IO_OPTS : {};
        const socketOpts = Object.assign({}, DEFAULT_SOCKET_OPTS, userSocketOpts);
        console.debug('Socket.IO options:', socketOpts);
        socket = io(socketOpts);
        // 将 socket 及合并后的 opts 挂载到全局以便其他模块(例如 chat.js)使用和调试
        try { window.socket = socket; window.SOCKET_IO_OPTS_MERGED = socketOpts; } catch (e) { /* ignore in restricted env */ }

        // 原生连接成功事件
        socket.on('connect', function() {
            console.log('socket connect OK, id=', socket.id);
            reconnectAttempts = 0;
            showToast('实时通知已连接', 'success');
        });

        // 应用层自定义connected事件（如果后端发出）
        socket.on('connected', function(data) {
            console.log('✓ 实时通知已就绪 (应用事件):', data);
            reconnectAttempts = 0;
        });

        // 连接错误
        socket.on('connect_error', function(err) {
            console.error('socket connect_error:', err);
            showToast('实时连接失败：' + (err && err.message ? err.message : '网络或权限问题'), 'error');
        });

        // 超时
        socket.on('connect_timeout', function(timeout) {
            console.warn('socket connect_timeout', timeout);
        });

        // 连接断开
        socket.on('disconnect', function(reason) {
            console.warn('✗ 实时通知已断开, reason=', reason);
            try { window.socket = null; } catch (e) {}
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
        
        // 心跳（安全捕获，避免由于 storage 被阻止导致抛异常）
        setInterval(function() {
            try {
                if (socket && socket.connected) {
                    socket.emit('ping');
                }
            } catch (e) {
                console.warn('发送心跳失败:', e);
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
            // 后备方案：使用非阻塞 DOM 通知替代 alert
            var container = document.getElementById('simple-toast-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'simple-toast-container';
                container.style.position = 'fixed';
                container.style.top = '10px';
                container.style.right = '10px';
                container.style.zIndex = '99999';
                document.body.appendChild(container);
            }
            var el = document.createElement('div');
            el.className = 'simple-toast';
            var bg = '#5bc0de';
            if (type === 'warning') bg = '#f0ad4e';
            if (type === 'error' || type === 'danger') bg = '#d9534f';
            el.style.background = bg;
            el.style.color = '#fff';
            el.style.padding = '8px 12px';
            el.style.marginTop = '6px';
            el.style.borderRadius = '4px';
            el.textContent = (title ? title + ': ' : '') + message;
            container.appendChild(el);
            setTimeout(function(){ try { container.removeChild(el); } catch(e){} }, 5000);
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
            if (!window.__storage_available) {
                showToast('浏览器阻止了存储访问，实时消息可能无法发送，请允许站点存储或禁用跟踪防护', 'warning');
                return false;
            }
            if (socket && socket.connected) {
                try {
                    socket.emit(event, data);
                    return true;
                } catch (e) {
                    console.error('发送 socket 事件失败', e);
                    showToast('发送消息失败：' + (e && e.message ? e.message : '未知错误'), 'error');
                    return false;
                }
            } else {
                showToast('未连接到实时服务，无法发送，请检查网络或稍后重试', 'warning');
                return false;
            }
        },
        joinDepartment: function(departmentId) {
            if (socket && socket.connected) {
                socket.emit('join_department', { department_id: departmentId });
            } else {
                console.warn('无法加入部门房间: 未连接');
            }
        },
        leaveDepartment: function(departmentId) {
            if (socket && socket.connected) {
                socket.emit('leave_department', { department_id: departmentId });
            } else {
                console.warn('无法离开部门房间: 未连接');
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
