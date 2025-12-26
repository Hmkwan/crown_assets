(function() {
    'use strict';

    // 如果主脚本因语法错误未能定义 RealtimeNotification，则使用最小后备实现。
    if (typeof window.RealtimeNotification === 'undefined') {
        console.warn('RealtimeNotification 未定义，启用后备 stub（来自 realtime-notifications-fallback.js）');

        // 最简单的 stub：记录调用并防止页面调用抛异常
        var fallback = {
            socket: function() { return null; },
            send: function(event, data) {
                console.warn('[Realtime Stub] send called:', event, data);
                return false;
            },
            joinDepartment: function(departmentId) {
                console.warn('[Realtime Stub] joinDepartment:', departmentId);
            },
            leaveDepartment: function(departmentId) {
                console.warn('[Realtime Stub] leaveDepartment:', departmentId);
            }
        };

        window.RealtimeNotification = fallback;
    }
})();
