// Message.jsx
import React from 'react';
import CopyButton from './CopyButton';

const Message = ({ content, isUser }) => {
  const userEmail = document.querySelector('.user-email')?.textContent;
  const userAvatar = userEmail?.[0]?.toUpperCase();

  const botAvatarSvg = (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M6 4L14 20" stroke="#0099FF" strokeWidth="3" strokeLinecap="round"/>
      <path d="M14 4L22 20" stroke="#0099FF" strokeWidth="3" strokeLinecap="round"/>
    </svg>
  );

  return (
    <div className="message relative">
      <div className={`avatar ${isUser ? 'user-avatar' : 'bot-avatar'}`}>
        {isUser ? userAvatar : botAvatarSvg}
      </div>
      <div className="message-content">
        {content}
      </div>
      {!isUser && <CopyButton content={content} />}
    </div>
  );
};

export default Message;