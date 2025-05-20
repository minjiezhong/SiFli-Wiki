// docs/source/_static/chatbot.js
window.difyChatbotConfig = {
    token: 'Mu1GufSBWxh9YgEJ',
    baseUrl: 'http://ai.sifli.com:8008'
};

const script = document.createElement('script');
script.src = 'http://ai.sifli.com:8008/embed.min.js';
script.id = 'Mu1GufSBWxh9YgEJ';
script.defer = true;
document.body.appendChild(script);

const style = document.createElement('style');
style.textContent = `
    #dify-chatbot-bubble-button {
        position: fixed;
        right: 20rem !important;
        top: 16rem !important;
        width: 48px !important;
        height: 48px !important;
        background-color: #1C64F2 !important;
        border: 2px solid white; /* 添加边框 */
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999; /* 确保在最顶层 */;
    }
          /* 添加移动端适配 */
    @media (max-width: 768px) {
        #dify-chatbot-bubble-button {
        top: 40rem !important;
        right: 2rem !important;
        width: 40px !important;
        height: 40px !important;
        }

        #dify-chatbot-bubble-window {
        width: 50% !important;
        height: 50% !important;
        max-height: none !important;
        bottom: 80px !important;
        right: 0 !important;
        }
    }
    #dify-chatbot-bubble-window {
        width: 24rem !important;
        height: 40rem !important;
    }
`;
document.head.appendChild(style);
