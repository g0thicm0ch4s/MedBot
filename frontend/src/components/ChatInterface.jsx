import React, { useState, useEffect } from 'react';
import './ChatInterface.css';

const DISCLAIMER = `⚠️ IMPORTANT: I provide general information only and cannot replace professional medical advice. For emergencies, call your local emergency number immediately.`;

// Helper to generate a UUID (v4, simple version)
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

function ChatInterface() {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: "Hello! I'm MedBot, your preliminary health assistant. How are you feeling today? Please describe your symptoms." }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [userId, setUserId] = useState(null);

  useEffect(() => {
    let uid = localStorage.getItem('medbot_user_id');
    if (!uid) {
      uid = generateUUID();
      localStorage.setItem('medbot_user_id', uid);
    }
    setUserId(uid);
  }, []);

  const sendMessage = async () => {
    if (!input.trim() || !userId) return;
    const userMsg = { sender: 'user', text: input };
    setMessages(msgs => [...msgs, userMsg]);
    setInput('');
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, user_id: userId })
      });
      if (!res.ok) throw new Error('Network response was not ok');
      const data = await res.json();
      setMessages(msgs => [...msgs, { sender: 'bot', text: data.response }]);
    } catch (err) {
      setMessages(msgs => [...msgs, { sender: 'bot', text: "Sorry, I couldn't reach the MedBot server. Please try again later." }]);
    }
    setLoading(false);
  };

  const handleInputKeyDown = (e) => {
    if (e.key === 'Enter') sendMessage();
  };

  return (
    <div className="medbot-chat-container">
      <div className="medbot-header">MedBot</div>
      <div className="medbot-disclaimer">{DISCLAIMER}</div>
      <div className="medbot-messages">
        {messages.map((msg, idx) => (
          msg.sender === 'bot' ? (
            <div
              key={idx}
              className={`medbot-message ${msg.sender}`}
              dangerouslySetInnerHTML={{ __html: msg.text.replace(/\n/g, '<br />') }}
            />
          ) : (
            <div key={idx} className={`medbot-message ${msg.sender}`}>{msg.text}</div>
          )
        ))}
        {loading && <div className="medbot-message bot loading">MedBot is typing...</div>}
      </div>
      <div className="medbot-input-row">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleInputKeyDown}
          placeholder="Type your message..."
          className="medbot-input"
          disabled={loading}
        />
        <button onClick={sendMessage} className="medbot-send-btn" disabled={loading}>Send</button>
      </div>
    </div>
  );
}

export default ChatInterface; 