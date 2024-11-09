# template.py

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="ngrok-skip-browser-warning" content="true">
    <title>NCS Internship AI Chatbot</title>
    <style>
        :root[data-theme="light"] {
            --bg-color: #FFFFFF;
            --text-color: #1C1C1C;
            --input-bg: #F0F0F0;
            --border-color: #1F2937;  /* Much darker - almost black */
            --hover-color: #F5F5F5;
            --tool-button-bg: #F3F4F6;
            --tool-button-hover: #E5E7EB;
            --avatar-bg: #E0E0E0;
            --chat-bg: #FFFFFF;
            --sidebar-border: #1F2937;  /* Much darker */
            --chat-border: #111827;  /* Almost black */
            --theme-button-bg: #F3F3F3;
            --theme-button-text: #333333;
        }

        :root[data-theme="dark"] {
            --bg-color: #1C1C1C;
            --text-color: #FFFFFF;
            --input-bg: #2D2D2D;
            --border-color: #1F2937;  /* Darker border */
            --hover-color: #2D2D2D;
            --tool-button-bg: #374151;
            --tool-button-hover: #4B5563;
            --avatar-bg: #3D3D3D;
            --chat-bg: #242424;
            --sidebar-border: #1F2937;  /* Darker border */
            --chat-border: #111827;  /* Almost black */
            --theme-button-bg: #383838;
            --theme-button-text: #FFFFFF;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            height: 100vh;
            margin: 0;
            padding: 0;
            overflow-x: hidden;
        }

        .sidebar-trigger {
            position: fixed;
            left: 0;
            top: 0;
            bottom: 0;
            width: 10px;
            z-index: 999;
            background: transparent;
        }

        .sidebar {
            position: fixed;
            left: -260px;
            top: 0;
            bottom: 0;
            width: 260px;
            background-color: var(--bg-color);
            border-right: 1px solid var(--sidebar-border);
            box-shadow: 2px 0 5px rgba(0, 0, 0, 0.05);
            display: flex;
            flex-direction: column;
            padding: 1rem;
            overflow-y: auto;
            overflow-x: hidden;
            z-index: 1000;
            transition: transform 0.3s ease;
        }

        .sidebar:hover,
        .sidebar-trigger:hover + .sidebar {
            transform: translateX(260px);
        }

        .main-content {
            margin-left: 10px;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            position: relative;
            max-width: 100%;
            transition: margin-left 0.3s ease;
            padding: 0 1rem;
        }

        .chat-container {
            max-width: 768px;
            width: 100%;
            margin: 1rem auto;
            padding: 2rem;
            padding-bottom: 180px;
            flex-grow: 1;
            position: relative;
            z-index: 1;
            background-color: var(--chat-bg);
            border: 1px solid var(--chat-border);
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .greeting {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border-color);
        }

        .greeting-logo {
            display: inline-flex;
            align-items: center;
            margin-right: 1rem;
        }

        .greeting-logo svg {
            width: 24px;
            height: 24px;
        }

        .greeting-logo svg path {
            stroke: #0099FF;
            stroke-linecap: round;
        }

        .greeting-text {
            font-size: 2rem;
            color: var(--text-color);
        }

        .input-container {
            position: fixed;
            bottom: 0;
            right: 0;
            width: calc(100% - 10px);
            background-color: var(--chat-bg);
            border-top: 2px solid var(--border-color); /* Changed from 1px to 2px */
            box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
            z-index: 1000;
        }

        .input-wrapper {
            max-width: 768px;
            margin: 0 auto;
            padding: 1rem;
            background-color: var(--chat-bg);
            border-radius: 8px;
        }

        .input-box {
            width: 100%;
            min-height: 60px;
            background-color: var(--input-bg);
            border: 2px solid var(--border-color); /* Changed from 1px to 2px */
            border-radius: 8px;
            color: var(--text-color);
            font-size: 1rem;
            resize: none;
            outline: none;
            padding: 1rem;
            margin-bottom: 1rem;
            transition: border-color 0.2s ease;
        }

        .input-box:focus {
            border-color: var(--chat-border);
        }

        .tools {
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
            justify-content: center;
            margin: 0 auto;
            padding: 0.5rem 0;
        }

        .tool-button {
            background-color: var(--tool-button-bg);
            color: var(--text-color);
            border: 3px solid var(--border-color); /* Increased from 2px to 3px */
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.2s ease;
            white-space: nowrap;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        }

        .tool-button:hover {
            background-color: var(--tool-button-hover);
            border-color: var(--chat-border);
            transform: translateY(-1px);
        }

        .message {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            animation: fadeIn 0.3s ease-in;
            padding: 1rem;
            border-radius: 8px;
            background-color: var(--bg-color);
            border: 1px solid var(--chat-border);
        }

        .avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: var(--avatar-bg);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            flex-shrink: 0;
            border: 1px solid var(--border-color);
        }

        .message-content {
            flex: 1;
            line-height: 1.5;
            color: var(--text-color);
        }

        .sidebar-header {
            margin-bottom: 1rem;
            white-space: nowrap;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border-color);
        }

        .new-chat-button {
            background-color: transparent;
            color: #0099FF;
            border: none;
            padding: 0.5rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
            white-space: nowrap;
            border-radius: 0.5rem;
            transition: background-color 0.2s;
        }

        .new-chat-button:hover {
            background-color: var(--hover-color);
        }

        .section-title {
            color: #888;
            font-size: 0.9rem;
            margin: 1.5rem 0 0.5rem;
            white-space: nowrap;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border-color);
        }

        .chat-list {
            width: 100%;
        }

        .chat-item {
            padding: 0.5rem;
            cursor: pointer;
            border-radius: 0.3rem;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--text-color);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 230px;
            border: 1px solid transparent;
            transition: all 0.2s ease;
        }

        .chat-item:hover {
            border-color: var(--border-color);
            background-color: var(--hover-color);
        }

        .chat-icon {
            opacity: 0.7;
        }

        .user-profile {
            margin-top: auto;
            padding: 1rem;
            border-top: 1px solid var(--border-color);
            background-color: var(--bg-color);
            width: 100%;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .user-avatar {
            width: 30px;
            height: 30px;
            background-color: var(--avatar-bg);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            flex-shrink: 0;
            border: 1px solid var(--border-color);
        }

        .user-email {
            font-size: 0.9rem;
            color: var(--text-color);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            max-width: 180px;
        }

        .theme-toggle {
            position: fixed;
            top: 1rem;
            right: 2rem;
            padding: 0.6rem 1.2rem;
            background-color: var(--theme-button-bg);
            color: var(--theme-button-text);
            border: 1px solid var(--border-color);
            border-radius: 0.5rem;
            cursor: pointer;
            z-index: 1001;
            font-weight: 500;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            transition: all 0.2s ease;
        }

        .theme-toggle:hover {
            background-color: var(--tool-button-hover);
            border-color: var(--chat-border);
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 1200px) {
            .main-content {
                max-width: 800px;
                padding: 0 2rem;
            }
        }

        @media (max-width: 768px) {
            .sidebar {
                transform: translateX(-100%);
                transition: transform 0.3s ease;
            }
            
            .sidebar.active {
                transform: translateX(0);
            }
            
            .main-content {
                margin-left: 0;
            }
            
            .input-container {
                width: 100%;
            }
            
            .chat-container {
                padding: 1rem;
            }
        }
    </style>
</head>
<body data-theme="light">
    <button class="theme-toggle" id="themeToggle">
        Switch Theme
    </button>
    <div class="sidebar-trigger"></div>
    <div class="sidebar">
        <div class="sidebar-header">
            <button class="new-chat-button">
                <span>⊕</span>
                Start new chat
            </button>
        </div>

        <div class="section-title">Starred</div>
        <div class="chat-list">
            <div class="chat-item">Star projects and chats you use often</div>
        </div>

        <div class="section-title">Recents</div>
        <div class="chat-list">
            <div class="chat-item">
                <span class="chat-icon">⊙</span>
                Setting up ngrok for public web access
            </div>
            <div class="chat-item">
                <span class="chat-icon">⊙</span>
                QA Tester Internship Tasks
            </div>
            <div class="chat-item">
                <span class="chat-icon">⊙</span>
                Telegram ChatBot Setup
            </div>
        </div>

        <div class="user-profile">
            <div class="user-avatar">M</div>
            <div class="user-email">user@example.com</div>
        </div>
    </div>
    <div class="main-content">
        <div class="chat-container" id="chatContainer">
            <div class="greeting">
                <div class="greeting-logo">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M6 4L14 20" stroke="#0099FF" stroke-width="3" stroke-linecap="round"/>
                        <path d="M14 4L22 20" stroke="#0099FF" stroke-width="3" stroke-linecap="round"/>
                    </svg>
                </div>
                <h1 class="greeting-text">Having a late night?</h1>
            </div>

            <div id="messagesList"></div>
        </div>

        <div class="input-container">
            <div class="input-wrapper">
                <div class="input-group">
                    <button id="fileButton" class="file-button">
                        <span class="file-icon">📎</span>
                        <input type="file" id="fileInput" style="display: none">
                    </button>
                    <textarea 
                        class="input-box" 
                        placeholder="How can I help you today?"
                        id="userInput"
                    ></textarea>
                    <button id="sendButton" class="send-button">
                        <span class="send-icon">➤</span>
                    </button>
                </div>
                <div id="filePreview" class="file-preview"></div>
                <div class="input-footer">
                    <div class="tools">
                        <button class="tool-button">Add content</button>
                        <button class="tool-button">Generate interview questions</button>
                        <button class="tool-button">Generate excel formulas</button>
                    </div>
                </div>
            </div>
        </div>
    </div>


    <style>
        .input-group {
            display: flex;
            gap: 0.5rem;
            align-items: flex-start;
            margin-bottom: 1rem;
        }
        .file-button {
            background-color: var(--tool-button-bg);
            color: var(--text-color);
            border: none;
            border-radius: 8px;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
            flex-shrink: 0;
            margin-top: 10px;
        }

        .file-button:hover {
            background-color: var(--tool-button-hover);
            transform: translateY(-1px);
        }

        .file-icon {
            font-size: 1.2rem;
        }

        .file-preview {
            margin: 0.5rem 0;
            padding: 0.5rem;
            border-radius: 4px;
            font-size: 0.9rem;
            display: none;
        }

        .file-preview.active {
            display: block;
            background-color: var(--tool-button-bg);
            border: 1px solid var(--border-color);
        }

        .file-preview-content {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .file-remove {
            color: #EF4444;
            cursor: pointer;
            font-weight: bold;
        }

        .numbered-list {
            list-style-type: decimal;
            padding-left: 1.5rem;
            margin: 0.5rem 0;
        }
        
        .send-button {
            background-color: #0099FF;
            color: white;
            border: none;
            border-radius: 8px;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
            flex-shrink: 0;
            margin-top: 10px;
        }

        .send-button:hover {
            background-color: #007ACC;
            transform: translateY(-1px);
        }

        .send-icon {
            font-size: 1.2rem;
        }
    </style>

    <script>
        const userInput = document.getElementById('userInput');
        const messagesList = document.getElementById('messagesList');
        const chatContainer = document.getElementById('chatContainer');
        const sendButton = document.getElementById('sendButton');
        const fileButton = document.getElementById('fileButton');
        const fileInput = document.getElementById('fileInput');
        const filePreview = document.getElementById('filePreview');
        const greetingText = document.querySelector('.greeting-text');  // Changed from getElementById
        const sidebar = document.querySelector('.sidebar');
        const sidebarTrigger = document.querySelector('.sidebar-trigger');
        const themeToggle = document.getElementById('themeToggle');
        const body = document.body;

        // Set greeting based on time
        function setGreeting() {
            const hour = new Date().getHours();
            if (hour >= 5 && hour < 12) {
                greetingText.textContent = 'Good morning';
            } else if (hour >= 12 && hour < 18) {
                greetingText.textContent = 'Good afternoon';
            } else {
                greetingText.textContent = 'Having a late night?';
            }
        }

        setGreeting();
        setInterval(setGreeting, 60000);

        function addMessage(content, isUser = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message';
            
            const avatar = document.createElement('div');
            avatar.className = 'avatar';
            avatar.textContent = isUser ? 'U' : 'C';
            
            const messageContent = document.createElement('div');
            messageContent.className = 'message-content';

            if (!isUser && (content.toLowerCase().includes('hello') || content.toLowerCase().includes('hi'))) {
                const greetingPart = content.split('\\n')[0];
                const options = [
                    "How can I assist you with technical documentation?",
                    "Would you like help with coding or system design?",
                    "Need assistance with project planning or troubleshooting?"
                ];
                
                messageContent.innerHTML = `
                    ${greetingPart}
                    <ol class="numbered-list">
                        ${options.map(option => `<li>${option}</li>`).join('')}
                    </ol>
                `;
            } else {
                messageContent.textContent = content;
            }
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(messageContent);
            messagesList.appendChild(messageDiv);
            
            // Scroll to bottom of chat
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;
            
            try {
                console.log('Sending message:', message);
                // Show user message immediately
                addMessage(message, true);
                userInput.value = '';
                userInput.style.height = 'auto';

                // Send request to server
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'ngrok-skip-browser-warning': 'true'
                    },
                    body: JSON.stringify({ message })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                console.log('Response data:', data);
                addMessage(data.response);
            } catch (error) {
                console.error('Error:', error);
                addMessage('Sorry, there was an error processing your message. Please try again.');
            }
        }

        // File handling
        fileButton.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                filePreview.innerHTML = `
                    <div class="file-preview-content">
                        <span>📄 ${file.name}</span>
                        <span class="file-remove" onclick="removeFile()">✕</span>
                    </div>
                `;
                filePreview.classList.add('active');
            }
        });

        function removeFile() {
            fileInput.value = '';
            filePreview.innerHTML = '';
            filePreview.classList.remove('active');
        }

        // Single event listener for Enter key
        userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Single event listener for send button
        sendButton.addEventListener('click', (e) => {
            e.preventDefault();
            sendMessage();
        });

        // Auto-resize textarea
        userInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });

        // Theme handling
        const savedTheme = localStorage.getItem('theme') || 'light';
        body.setAttribute('data-theme', savedTheme);
        themeToggle.textContent = `Switch to ${savedTheme === 'light' ? 'Dark' : 'Light'} Theme`;

        themeToggle.addEventListener('click', () => {
            const currentTheme = body.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            themeToggle.textContent = `Switch to ${newTheme === 'light' ? 'Dark' : 'Light'} Theme`;
        });

        // Sidebar functionality
        let isOverSidebar = false;

        sidebar.addEventListener('mouseenter', () => {
            isOverSidebar = true;
            sidebar.style.transform = 'translateX(260px)';
        });

        sidebar.addEventListener('mouseleave', () => {
            isOverSidebar = false;
            setTimeout(() => {
                if (!isOverSidebar) {
                    sidebar.style.transform = 'translateX(0)';
                }
            }, 300);
        });

        // Chat functionality
        document.querySelector('.new-chat-button').addEventListener('click', () => {
            messagesList.innerHTML = '';
            userInput.value = '';
            userInput.style.height = 'auto';
        });

        document.querySelectorAll('.chat-item').forEach(item => {
            item.addEventListener('click', () => {
                console.log('Loading chat:', item.textContent.trim());
            });
        });
    </script>
</body>
</html>
'''