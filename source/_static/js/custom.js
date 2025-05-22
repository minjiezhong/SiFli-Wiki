document.addEventListener('DOMContentLoaded', function() {
    var links = document.querySelectorAll('a');
    var currentHost = window.location.hostname;

    links.forEach(function(link) {
        var href = link.href;
        try {
            var linkUrl = new URL(href);
            // 检查是否为外部链接
            if (linkUrl.hostname !== currentHost && (href.startsWith('http:') || href.startsWith('https:'))) {
                link.setAttribute('target', '_blank');
                link.setAttribute('rel', 'noopener noreferrer');
            }
        } catch(e) {
            // 处理无效URL
        }
    });
});
