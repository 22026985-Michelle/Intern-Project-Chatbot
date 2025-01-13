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
            --input-container-bg: #FFFFFF;
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
            --input-container-bg: #1C1C1C;
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
            overflow-y: auto;
            min-height: 0; 
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
        }

        .chat-item:hover {
            border-color: var(--border-color);
            background-color: var(--hover-color);
        }

        .chat-item:hover .chat-actions {
            opacity: 1;
        }   

        .chat-action-button {
            background: none;
            border: none;
            padding: 0.25rem;
            cursor: pointer;
            color: var(--text-color);
            opacity: 0.7;
            transition: opacity 0.2s ease;
        }

            
        .chat-action-button:hover {
            opacity: 1;
        }

        .placeholder-text {
            color: var(--text-color);
            opacity: 0.7;
            cursor: default;
        }

        .placeholder-text:hover {
            background-color: transparent;
        }

        .chat-item.active {
            background-color: var(--hover-color);
            border-color: var(--send-button-bg);
        }

        .chat-title {
            flex-grow: 1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .chat-icon {
            opacity: 0.7;
        }

        .user-profile {
            position: relative;
            padding: 1rem;
            border-top: 1px solid var(--border-color);
            background-color: var(--bg-color);
            width: 100%;
            z-index: 1011;
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
            z-index: 1010;
            transform: translateX(0);
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            height: 100vh;
        }

        .sidebar-content {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
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
            transition: margin-left 0.3s ease;
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

        .chat-actions {
            display: flex;
            gap: 0.5rem;
            opacity: 0;
            transition: opacity 0.2s ease;
        }

        /* Input Container Styles */
        .input-container {
            position: fixed;
            bottom: 0;
            right: 0;
            width: 100%;  /* Remove the calculation */
            margin-left: 0;  /* Remove margin */
            background-color: var(--input-container-bg);
            border-top: 2px solid var(--input-container-border);
            z-index: 1000;
        }

        .sidebar:not(:hover) + .main-content .input-container {
            width: 100%;
            transform: translateX(0);
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

        .profile-button {
            background: none;
            border: none;
            padding: 0.5rem;
            width: 100%;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            cursor: pointer;
            transition: background-color 0.2s ease;
            border-radius: 0.5rem;
            color: var(--text-color); 
        }

        .profile-button:hover {
            background-color: var(--hover-color);
        }

        .profile-menu {
            position: absolute;
            bottom: 100%;
            left: 1rem;
            width: 200px;
            background-color: var(--bg-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            box-shadow: 0 2px 10px var(--box-shadow);
            margin-bottom: 0.5rem;
            z-index: 1012;
            opacity: 0;
            pointer-events: none;
            transform: translateY(10px);
            transition: opacity 0.2s ease, transform 0.2s ease;
        }

        .profile-menu.active {
            opacity: 1;
            pointer-events: auto;
            transform: translateY(0);
        }

        .menu-item {
            width: 100%;
            padding: 0.75rem 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: none;
            border: none;
            color: var(--text-color);
            cursor: pointer;
            text-align: left;
            transition: background-color 0.2s ease;
        }

        .menu-item:hover {
            background-color: var(--hover-color);
        }

        .menu-icon {
            font-size: 1.2rem;
        }

        .appearance-menu {
            padding: 0.5rem 0;
            border-top: 1px solid var(--border-color);
            display: none;
        }

        .appearance-menu.active {
            display: block;
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
    <div class="sidebar-trigger"></div>
    <div class="sidebar">
        <div class="sidebar-content">
            <div class="sidebar-header">
                <button class="new-chat-button" id="newChatButton">
                    <span>⊕</span>
                    Start new chat
                </button>
            </div>

            <div class="section-title">Recents</div>
            <div class="chat-list" id="recentChats">
                <div class="chat-item placeholder-text">No recent chats yet</div>
            </div>
        </div>
        
        <div class="user-profile" id="userProfile">
            <button class="profile-button" id="profileButton">
                <div class="user-avatar">{avatar_letter}</div>
                <div class="user-email">{email}</div>
            </button>
            <div class="profile-menu" id="profileMenu">
                <button class="menu-item" onclick="window.location.href='https://internproject-4fq7.onrender.com/Settings'">
                    <span class="menu-icon">⚙️</span>
                    Settings
                </button>
                <button class="menu-item" onclick="toggleAppearanceMenu()">
                    <span class="menu-icon">🎨</span>
                    Appearance
                </button>
                <div class="appearance-menu" id="appearanceMenu">
                    <button class="menu-item" onclick="setTheme('light')">
                        <span class="menu-icon">☀️</span>
                        Light
                    </button>
                    <button class="menu-item" onclick="setTheme('dark')">
                        <span class="menu-icon">🌙</span>
                        Dark
                    </button>
                </div>
            </div>
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
        // Chat Manager Class
        class ChatManager {
            constructor() {
                this.currentChatId = null;
                this.BASE_URL = 'https://internproject-4fq7.onrender.com';
                this.init();
            }

            init() {
                this.bindEvents();
                this.loadRecentChats();
            }

            bindEvents() {
                // New chat button
                document.getElementById('newChatButton').addEventListener('click', () => this.handleNewChat());
                
                // Send button and input
                document.getElementById('sendButton').addEventListener('click', () => this.sendMessage());
                document.getElementById('userInput').addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        this.sendMessage();
                    }
                });

                // File handling
                const fileButton = document.getElementById('fileButton');
                const fileInput = document.getElementById('fileInput');
                fileButton.addEventListener('click', () => fileInput.click());
                fileInput.addEventListener('change', this.handleFileSelect.bind(this));
            }

            async generateChatTitle(message) {
                try {
                    const response = await fetch(`${this.BASE_URL}/api/generate-title`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ message })
                    });

                    if (!response.ok) throw new Error('Failed to generate title');
                    const data = await response.json();
                    return data.title;
                } catch (error) {
                    console.error('Error generating title:', error);
                    return 'New Chat';
                }
            }

            async createNewChat() {
                try {
                    const response = await fetch(`${this.BASE_URL}/api/create-chat`, {
                        method: 'POST'
                    });

                    if (!response.ok) throw new Error('Failed to create chat');
                    const data = await response.json();
                    
                    this.currentChatId = data.chat_id;
                    document.getElementById('messagesList').innerHTML = '';
                    document.getElementById('userInput').value = '';
                    
                    await this.loadRecentChats();
                } catch (error) {
                    console.error('Error creating chat:', error);
                }
            }

            async loadRecentChats() {
                try {
                    const response = await fetch(`${this.BASE_URL}/api/chat-history`, {
                        method: 'GET',
                        credentials: 'include',
                        headers: { 'Content-Type': 'application/json' }
                    });

                    const data = await response.json();
                    console.log('Chat history response:', data);

                    if (response.ok) {
                        // Update "Recents" and "Today" sections
                        this.updateRecentChats(data.chats.filter(chat => chat.section === 'Recents'));
                        this.updateTodayChat(data.chats.filter(chat => chat.section === 'Today'));
                    } else {
                        console.error('Error loading chats:', data.error);
                        this.updateRecentChats([]);
                        this.updateTodayChat([]);
                    }
                } catch (error) {
                    console.error('Error loading chats:', error);
                    this.updateRecentChats([]);
                    this.updateTodayChat([]);
                }
            }


            updateStarredChats(chats) {
                const starredSection = document.getElementById('starredChats');
                starredSection.innerHTML = '';
                
                if (chats.length === 0) {
                    starredSection.innerHTML = `
                        <div class="chat-item placeholder-text">
                            Star projects and chats you use often
                        </div>
                    `;
                    return;
                }

                chats.forEach(chat => {
                    starredSection.appendChild(this.createChatElement(chat));
                });
            }

            updateRecentChats(chats) {
                const recentSection = document.getElementById('recentChats');
                if (!recentSection) return;

                console.log('Updating Recent Chats:', chats); // Debugging

                recentSection.innerHTML = ''; // Clear existing chats

                if (chats.length === 0) {
                    recentSection.innerHTML = `<div class="chat-item placeholder-text">No recent chats yet</div>`;
                    return;
                }

                chats.forEach(chat => {
                    const chatElement = this.createChatElement(chat);
                    recentSection.appendChild(chatElement);
                });
            }

            updateSidebarChats(chats) {
                if (!Array.isArray(chats)) {
                    console.error("Expected chats to be an array", chats);
                    chats = [];
                }
                
                const recentChats = document.getElementById('recentChats');
                if (!recentChats) {
                    console.error("Could not find recentChats element");
                    return;
                }
                
                recentChats.innerHTML = '';
                chats.forEach(chat => {
                    const chatElement = this.createChatElement(chat);
                    recentChats.appendChild(chatElement);
                });
            }

            createChatElement(chat) {
                const div = document.createElement('div');
                div.className = 'chat-item';

                div.innerHTML = `
                    <span class="chat-title">${chat.title || 'New Chat'}</span>
                    <div class="chat-actions">
                        <button class="chat-action-button delete-button" title="Delete chat">🗑</button>
                    </div>
                `;

                // Handle click to load the chat
                div.querySelector('.chat-title').addEventListener('click', () => {
                    this.loadChat(chat.chat_id);
                });

                // Handle delete button
                div.querySelector('.delete-button').addEventListener('click', async (e) => {
                    e.stopPropagation();
                    await this.deleteChat(chat.chat_id);
                });

                return div;
            }


            async handleNewChat() {
                try {
                    // Move the current chat to "Recents" if it exists
                    if (this.currentChatId) {
                        await this.moveToRecents(this.currentChatId);
                    }

                    // Reset UI for the new chat
                    document.getElementById('messagesList').innerHTML = '';
                    document.getElementById('userInput').value = '';

                    // Reset current chat ID (new chat will be created on first message)
                    this.currentChatId = null;

                    // Update chat sections
                    await this.loadRecentChats();

                    console.log('New chat initialized');
                } catch (error) {
                    console.error('Error handling new chat:', error);
                }
            }

            async getChatMessages(chatId) {
                try {
                    const response = await fetch(`${this.BASE_URL}/api/chat/${chatId}/messages`);
                    if (!response.ok) throw new Error('Failed to get chat messages');
                    const data = await response.json();
                    return data.messages;
                } catch (error) {
                    console.error('Error getting chat messages:', error);
                    return [];
                }
            }

            async moveToRecents(chatId) {
                try {
                    // Update chat section to "Recents"
                    const response = await fetch(`${this.BASE_URL}/api/chat/${chatId}/section`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ section: 'Recents' })
                    });

                    if (!response.ok) throw new Error('Failed to move chat to recents');
                } catch (error) {
                    console.error('Error moving chat to recents:', error);
                }
            }

            async getRecentChats() {
                try {
                    const response = await fetch(`${this.BASE_URL}/api/chat-history`);
                    if (!response.ok) throw new Error('Failed to fetch chats');
                    const data = await response.json();
                    return data.chats || [];
                } catch (error) {
                    console.error('Error getting recent chats:', error);
                    return [];
                }
            }
                        
            async sendMessage() {
                const input = document.getElementById('userInput');
                const message = input.value.trim();
                if (!message) return;

                try {
                    // Create a new chat if this is the first message
                    if (!this.currentChatId) {
                        const createResponse = await fetch(`${this.BASE_URL}/api/create-chat`, {
                            method: 'POST',
                            credentials: 'include',
                            headers: { 'Content-Type': 'application/json' }
                        });

                        const creationData = await createResponse.json();
                        if (!createResponse.ok) throw new Error(creationData.error);

                        this.currentChatId = creationData.chat_id;

                        // Generate a dynamic title for the chat
                        const title = await this.generateChatTitle(message);
                        await this.updateChatTitle(this.currentChatId, title);

                        // Assign the chat to the "Today" section
                        await this.updateChatSection(this.currentChatId, 'Today');
                    }

                    // Add user message to the UI
                    this.addMessageToUI(message, true);
                    input.value = '';

                    // Send the message to the backend
                    const response = await fetch(`${this.BASE_URL}/api/chat`, {
                        method: 'POST',
                        credentials: 'include',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ chat_id: this.currentChatId, message })
                    });

                    const data = await response.json();
                    if (!response.ok) throw new Error(data.error);

                    // Add bot response to the UI
                    this.addMessageToUI(data.response, false);

                    // Refresh the sidebar
                    await this.loadRecentChats();
                } catch (error) {
                    console.error('Error sending message:', error);
                    this.addMessageToUI(`Error: ${error.message}`, false);
                }
            }


            addMessageToUI(content, isUser) {
                const messagesList = document.getElementById('messagesList');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message';
                messageDiv.innerHTML = `
                    <div class="avatar">${isUser ? 'U' : 'C'}</div>
                    <div class="message-content">${content}</div>
                `;
                messagesList.appendChild(messageDiv);
                messagesList.scrollTop = messagesList.scrollHeight;
            }

            async updateChatSection(chatId, section) {
                try {
                    const response = await fetch(`${this.BASE_URL}/api/chat/${chatId}/section`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ section })
                    });

                    if (!response.ok) throw new Error('Failed to update chat section');
                } catch (error) {
                    console.error('Error updating chat section:', error);
                }
            }

            async updateChatTitle(chatId, title) {
                try {
                    const response = await fetch(`${this.BASE_URL}/api/chat/${chatId}/title`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ title })
                    });
                    
                    if (!response.ok) throw new Error('Failed to update chat title');
                    await this.loadRecentChats();
                } catch (error) {
                    console.error('Error updating chat title:', error);
                }
            }

            async toggleStarChat(chatId, starred) {
                try {
                    const response = await fetch(`${this.BASE_URL}/api/chat/${chatId}/star`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        credentials: 'include',
                        body: JSON.stringify({ is_starred: starred })
                    });

                    if (!response.ok) throw new Error('Failed to update star status');

                    // Reload chat list to reflect changes
                    await this.loadRecentChats();
                } catch (error) {
                    console.error('Error starring chat:', error);
                }
            }

            async deleteChat(chatId) {
                if (!confirm('Are you sure you want to delete this chat?')) return;

                try {
                    const response = await fetch(`${this.BASE_URL}/api/chat/${chatId}`, {
                        method: 'DELETE',
                        credentials: 'include'
                    });

                    if (!response.ok) throw new Error('Failed to delete chat');

                    if (chatId === this.currentChatId) {
                        this.currentChatId = null;
                        document.getElementById('messagesList').innerHTML = '';
                    }

                    await this.loadRecentChats();
                } catch (error) {
                    console.error('Error deleting chat:', error);
                }
            }
            async loadChat(chatId) {
                try {
                    const response = await fetch(`${this.BASE_URL}/api/chat/${chatId}/messages`);
                    if (!response.ok) throw new Error('Failed to load chat messages');
                    
                    const data = await response.json();
                    this.currentChatId = chatId;
                    
                    const messagesList = document.getElementById('messagesList');
                    messagesList.innerHTML = ''; // Clear previous messages
                    
                    data.messages.forEach(message => {
                        this.addMessageToUI(message.content, message.is_user);
                    });
                } catch (error) {
                    console.error('Error loading chat:', error);
                }
            }

            updateTodayChat(chats) {
                const todaySection = document.getElementById('recentChats'); // Correct target
                if (!todaySection) return;

                todaySection.innerHTML = ''; // Clear the current sidebar content

                if (chats.length === 0) {
                    todaySection.innerHTML = `<div class="chat-item placeholder-text">No recent chats yet</div>`;
                    return;
                }

                chats.forEach(chat => {
                    const chatElement = this.createChatElement(chat);
                    todaySection.appendChild(chatElement);
                });
            }

            handleFileSelect(e) {
                const file = e.target.files[0];
                const filePreview = document.getElementById('filePreview');
                
                if (file) {
                    filePreview.innerHTML = `
                        <div class="file-preview-content">
                            <span>📄 ${file.name}</span>
                            <span class="file-remove" onclick="chatManager.removeFile()">✕</span>
                        </div>
                    `;
                    filePreview.classList.add('active');
                }
            }

            removeFile() {
                const fileInput = document.getElementById('fileInput');
                const filePreview = document.getElementById('filePreview');
                
                fileInput.value = '';
                filePreview.innerHTML = '';
                filePreview.classList.remove('active');
            }
        }

        // Single DOMContentLoaded event listener
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize DOM elements
            const userInput = document.getElementById('userInput');
            const messagesList = document.getElementById('messagesList');
            const chatContainer = document.getElementById('chatContainer');
            const sendButton = document.getElementById('sendButton');
            const fileButton = document.getElementById('fileButton');
            const fileInput = document.getElementById('fileInput');
            const filePreview = document.getElementById('filePreview');
            const greetingText = document.querySelector('.greeting-text');
            const sidebar = document.querySelector('.sidebar');
            const sidebarTrigger = document.querySelector('.sidebar-trigger');
            const body = document.body;
            const profileButton = document.getElementById('profileButton');
            const profileMenu = document.getElementById('profileMenu');
            const appearanceMenu = document.getElementById('appearanceMenu');

            let isMenuOpen = false;
            let isOverSidebar = false;
            let sidebarTimeout = null;

            // Initialize chat manager
            window.chatManager = new ChatManager();

            // Sidebar Control Functions
            function showSidebar() {
                if (sidebarTimeout) {
                    clearTimeout(sidebarTimeout);
                    sidebarTimeout = null;
                }
                sidebar.style.transform = 'translateX(260px)';
            }

            function hideSidebar() {
                if (!isMenuOpen) {
                    sidebar.style.transform = '';
                }
            }

            // Profile and Menu Functions
            function toggleProfileMenu(event) {
                if (event) {
                    event.stopPropagation();
                }
                isMenuOpen = !isMenuOpen;
                
                if (isMenuOpen) {
                    showSidebar();
                    profileMenu.classList.add('active');
                } else {
                    profileMenu.classList.remove('active');
                    appearanceMenu.classList.remove('active');
                    if (!isOverSidebar) {
                        hideSidebar();
                    }
                }
            }

            // Theme Functions
            function updateTheme(theme) {
                body.setAttribute('data-theme', theme);
                localStorage.setItem('theme', theme);
            }

            // Global Functions
            window.toggleAppearanceMenu = function() {
                appearanceMenu.classList.toggle('active');
            };
            
            window.setTheme = function(theme) {
                body.setAttribute('data-theme', theme);
                localStorage.setItem('theme', theme);
                
                isMenuOpen = false;
                profileMenu.classList.remove('active');
                appearanceMenu.classList.remove('active');
                if (!isOverSidebar) {
                    hideSidebar();
                }
            };

            window.setMessage = function(message) {
                userInput.value = message;
                userInput.focus();
            };

            // Event Listeners
            profileButton.addEventListener('click', toggleProfileMenu);

            document.addEventListener('click', (event) => {
                const isClickInsideProfile = profileButton.contains(event.target);
                const isClickInsideMenu = profileMenu.contains(event.target);
                const isClickInsideSidebar = sidebar.contains(event.target);

                if (!isClickInsideProfile && !isClickInsideMenu && !isClickInsideSidebar && isMenuOpen) {
                    toggleProfileMenu();
                }
            });

            sidebarTrigger.addEventListener('mouseenter', () => {
                isOverSidebar = true;
                showSidebar();
            });

            sidebarTrigger.addEventListener('mouseleave', () => {
                isOverSidebar = false;
                if (!isMenuOpen) {
                    sidebarTimeout = setTimeout(hideSidebar, 300);
                }
            });

            // Initialize theme and greeting
            let currentTheme = localStorage.getItem('theme') || 'light';
            updateTheme(currentTheme);
            
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
        });
    </script>
</body>
</html>
'''