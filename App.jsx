import { useState } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [mood, setMood] = useState('default');

  const detectMood = (text) => {
    const sadWords = ['sad', 'unhappy', 'depressed', 'chill', 'focus', 'sleep'];
    const happyWords = ['happy', 'energetic', 'excited', 'cheerful', 'glad'];
    const angryWords = ['angry', 'mad', 'furious', 'romantic', 'frustrated'];
    
    if (sadWords.some((word) => text.toLowerCase().includes(word))) {
      return 'sad';
    } else if (happyWords.some((word) => text.toLowerCase().includes(word))) {
      return 'happy';
    } else if (angryWords.some((word) => text.toLowerCase().includes(word))) {
      return 'angry';
    }
    return 'default';
  };

  const handleSendMessage = () => {
    if (input.trim()) {
      const newMood = detectMood(input);
      setMood(newMood);
      setMessages([...messages, { text: input, sender: 'user' }]);
      setInput('');
      // Simulate bot response
      setTimeout(() => {
        setMessages((prevMessages) => [...prevMessages, { text: 'Hello! How can I assist you?', sender: 'bot' }]);
      }, 1000);
    }
  };

  return (
    <div className={`app-container ${mood}`}>
      <div className="bg-gradient"></div>
      <div className="bg-noise"></div>
      <div className="chatbot-wrapper">
        <div className="title-container">
          <h1 className="title">Mood Music</h1>
        </div>
        <div className="chat-container">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.sender}`}>
              {msg.text}
            </div>
          ))}
        </div>
        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
          />
          <button onClick={handleSendMessage}>Send</button>
        </div>
      </div>
    </div>
  );
}

export default App;
