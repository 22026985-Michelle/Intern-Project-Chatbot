# template.py

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NCS Internship AI Chatbot</title>
    <style>
        /* Theme Variables */
        :root[data-theme="light"] {
            --bg-color: #FFFFFF;
            --text-color: #1C1C1C;
            --input-bg: #F0F0F0;
            --border-color: #E5E7EB;
            --hover-color: #F5F5F5;
            --tool-button-bg: #F3F4F6;
            --tool-button-hover: #E5E7EB;
            --avatar-bg: #E0E0E0;
            --chat-bg: #FFFFFF;
            --sidebar-border: #E5E7EB;
            --chat-border: #E5E7EB;
            --theme-button-bg: #F3F3F3;
            --theme-button-text: #333333;
            --message-bg: #F9FAFB;
            --send-button-bg: #0099FF;
            --send-button-hover: #007ACC;
            --input-container-bg: rgba(255, 255, 255, 0.9);
            --input-container-border: #E5E7EB;
            --box-shadow: rgba(0, 0, 0, 0.05);
        }

        :root[data-theme="dark"] {
            --bg-color: #1C1C1C;
            --text-color: #FFFFFF;
            --input-bg: #2D2D2D;
            --border-color: #4B5563;
            --hover-color: #2D2D2D;
            --tool-button-bg: #374151;
            --tool-button-hover: #4B5563;
            --avatar-bg: #3D3D3D;
            --chat-bg: #1C1C1C;
            --sidebar-border: #4B5563;
            --chat-border: #4B5563;
            --theme-button-bg: #374151;
            --theme-button-text: #FFFFFF;
            --message-bg: #2D2D2D;
            --send-button-bg: #0099FF;
            --send-button-hover: #007ACC;
            --input-container-bg: rgba(28, 28, 28, 0.95);
            --input-container-border: #4B5563;
            --box-shadow: rgba(0, 0, 0, 0.2);
        }

        /* Global Styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            transition: background-color 0.3s ease, 
                      color 0.3s ease, 
                      border-color 0.3s ease,
                      transform 0.3s ease,
                      box-shadow 0.3s ease;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            height: 100vh;
            margin: 0;
            padding: 0;
            overflow-x: hidden;
        }

        /* Sidebar Styles */
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
            box-shadow: 2px 0 10px var(--box-shadow);
            display: flex;
            flex-direction: column;
            padding: 1rem;
            overflow-y: auto;
            overflow-x: hidden;
            z-index: 1000;
            transform: translateX(0);
            transition: transform 0.3s ease;
        }

        .sidebar:hover,
        .sidebar-trigger:hover + .sidebar {
            transform: translateX(260px);
        }

        /* Main Content Styles */
        .main-content {
            margin-left: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            position: relative;
            max-width: 100%;
            padding: 0 1rem;
        }

        /* Chat Container Styles */
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
            border-radius: 8px;
        }

        /* Input Container Styles */
        .input-container {
            position: fixed;
            bottom: 0;
            right: 0;
            width: 100%;
            background-color: var(--input-container-bg);
            border-top: 2px solid var(--input-container-border);
            backdrop-filter: blur(10px);
            z-index: 1000;
        }

        .input-wrapper {
            max-width: 768px;
            margin: 0 auto;
            padding: 1rem;
            background-color: transparent;
            border-radius: 8px;
        }

        .input-group {
            display: flex;
            gap: 0.75rem;
            align-items: flex-start;
            margin-bottom: 1rem;
        }

        .input-box {
            width: 100%;
            min-height: 45px;
            background-color: var(--input-bg);
            color: var(--text-color);
            border: 2px solid var(--border-color);
            border-radius: 8px;
            font-size: 1rem;
            resize: none;
            outline: none;
            padding: 0.75rem;
            margin-bottom: 0;
            transition: all 0.3s ease;
        }

        .input-box:focus {
            border-color: var(--send-button-bg);
            box-shadow: 0 0 0 2px var(--box-shadow);
        }

        /* Button Styles */
        .send-button {
            background-color: var(--send-button-bg);
            color: white;
            border: none;
            border-radius: 8px;
            width: 45px;
            height: 45px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
            flex-shrink: 0;
            box-shadow: 0 2px 4px var(--box-shadow);
        }

        .send-button:hover {
            background-color: var(--send-button-hover);
            transform: translateY(-1px);
            box-shadow: 0 4px 6px var(--box-shadow);
        }

        .file-button {
            background-color: var(--tool-button-bg);
            color: var(--text-color);
            border: none;
            border-radius: 8px;
            width: 45px;
            height: 45px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
            flex-shrink: 0;
        }

        .file-button:hover {
            background-color: var(--tool-button-hover);
            transform: translateY(-1px);
        }

        /* Message Styles */
        .message {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            animation: fadeIn 0.3s ease-in;
            padding: 1rem;
            border-radius: 8px;
            background-color: var(--message-bg);
            border: 1px solid var(--border-color);
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

        /* Theme Toggle Button */
        .theme-toggle {
            position: fixed;
            top: 1rem;
            right: 2rem;
            padding: 0.6rem 1.2rem;
            background-color: var(--theme-button-bg);
            color: var(--theme-button-text);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            cursor: pointer;
            z-index: 1001;
            font-weight: 500;
            box-shadow: 0 2px 4px var(--box-shadow);
        }

        .theme-toggle:hover {
            background-color: var(--tool-button-hover);
            transform: translateY(-1px);
            box-shadow: 0 4px 6px var(--box-shadow);
        }

        /* Tool Buttons */
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
            border: 2px solid var(--border-color);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.2s ease;
            white-space: nowrap;
        }

        .tool-button:hover {
            background-color: var(--tool-button-hover);
            transform: translateY(-1px);
            border-color: var(--send-button-bg);
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Media Queries */
        @media (max-width: 768px) {
            .theme-toggle {
                top: 0.5rem;
                right: 0.5rem;
                padding: 0.4rem 0.8rem;
                font-size: 0.9rem;
            }

            .chat-container {
                padding: 1rem;
                margin: 0.5rem auto;
            }

            .tools {
                padding: 0.25rem 0;
            }

            .tool-button {
                padding: 0.4rem 0.8rem;
                font-size: 0.8rem;
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
                        <button class="tool-button" onclick="setMessage('Please help me convert the format of my data.')">Convert format of data</button>
                        <button class="tool-button" onclick="setMessage('Can you help me check my data for any issues?')">Check data</button>
                        <button class="tool-button" onclick="setMessage('I would like to learn more about NCS.')">Learn more about NCS</button>
                        <button class="tool-button" onclick="setMessage('Can you help me fill in the missing fields?')">Fill in fields</button>
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
            transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
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
            width: 45px;
            height: 45px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
            flex-shrink: 0;
            margin-top: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .send-button:hover {
            background-color: #007ACC;
            transform: translateY(-1px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .send-icon {
            font-size: 1.2rem;
        }
    </style>

    <script>
        const BASE_URL = 'https://internproject-4fq7.onrender.com';
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

        function setMessage(message) {
            const userInput = document.getElementById('userInput');
            userInput.value = message;
            userInput.focus();
        }

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
                addMessage(message, true);
                userInput.value = '';
                userInput.style.height = 'auto';

                const response = await fetch(`${BASE_URL}/chat`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    console.error('Server error:', errorData);
                    throw new Error(`Server error: ${errorData.details || errorData.error || 'Unknown error'}`);
                }

                const data = await response.json();
                console.log('Response data:', data);
                addMessage(data.response);
            } catch (error) {
                console.error('Error details:', error);
                addMessage(`Error: ${error.message || 'An unknown error occurred'}`);
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
        let currentTheme = localStorage.getItem('theme') || 'light';
        body.setAttribute('data-theme', currentTheme);
        themeToggle.textContent = `Switch to ${currentTheme === 'light' ? 'Dark' : 'Light'} Theme`;

        themeToggle.addEventListener('click', () => {
            currentTheme = currentTheme === 'light' ? 'dark' : 'light';
            body.setAttribute('data-theme', currentTheme);
            localStorage.setItem('theme', currentTheme);
            themeToggle.textContent = `Switch to ${currentTheme === 'light' ? 'Dark' : 'Light'} Theme`;
        });

        // Sidebar functionality
        let isOverSidebar = false;
        let sidebarTimeout;

        sidebar.addEventListener('mouseenter', () => {
            isOverSidebar = true;
            clearTimeout(sidebarTimeout);
            requestAnimationFrame(() => {
                sidebar.style.transform = 'translateX(260px)';
            });
        });

        sidebar.addEventListener('mouseleave', () => {
            isOverSidebar = false;
            sidebarTimeout = setTimeout(() => {
                if (!isOverSidebar) {
                    requestAnimationFrame(() => {
                        sidebar.style.transform = '';
                    });
                }
            }, 300);
        });

        sidebarTrigger.addEventListener('mouseenter', () => {
            isOverSidebar = true;
            clearTimeout(sidebarTimeout);
            requestAnimationFrame(() => {
                sidebar.style.transform = 'translateX(260px)';
            });
        });

        sidebarTrigger.addEventListener('mouseleave', () => {
            isOverSidebar = false;
            sidebarTimeout = setTimeout(() => {
                if (!isOverSidebar) {
                    requestAnimationFrame(() => {
                        sidebar.style.transform = '';
                    });
                }
            }, 300);
        });

        // Theme handling - Updated for reliable switching
        let currentTheme = localStorage.getItem('theme') || 'light';
        
        function updateTheme(theme) {
            body.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
            themeToggle.textContent = `Switch to ${theme === 'light' ? 'Dark' : 'Light'} Theme`;
        }

        updateTheme(currentTheme);

        themeToggle.addEventListener('click', () => {
            currentTheme = currentTheme === 'light' ? 'dark' : 'light';
            updateTheme(currentTheme);
        });

'''