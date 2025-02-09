import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [mood, setMood] = useState('default');
  const [songs, setSongs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const detectMood = (text) => {
    const moodMap = {
      Sad: ['sad', 'unhappy', 'depressed', 'melancholy', 'blue'],
      Happy: ['happy', 'energetic', 'excited', 'cheerful', 'joyful'],
      Angry: ['angry', 'mad', 'furious', 'annoyed', 'frustrated'],
      Chill: ['chill', 'relaxed', 'calm', 'peaceful', 'soft'],
      Focus: ['focus', 'study', 'concentrate', 'deep work'],
      Sleep: ['sleep', 'tired', 'relaxation', 'soothing'],
      Romantic: ['romantic', 'love', 'valentine', 'date night'],
      Roadtrip: ['roadtrip', 'driving', 'long ride', 'travel'],
      Party: ['party', 'dance', 'night out', 'celebration'],
      Workout: ['workout', 'gym', 'exercise', 'pump up'],
    };

    for (const [moodKey, words] of Object.entries(moodMap)) {
      if (words.some((word) => text.toLowerCase().includes(word))) {
        return moodKey;
      }
    }
    return 'default';
  };

  const fetchSongs = async (refresh = false) => {
    if (!mood.trim() && !refresh) return;

    setLoading(true);
    setError('');

    try {
      const queryMood = refresh ? mood : detectMood(input);
      setMood(queryMood);

      console.log(`Fetching songs for mood: ${queryMood} (refresh: ${refresh})`);

      const response = await axios.get(
        `http://127.0.0.1:8000/chat?mood=${queryMood}&refresh=${refresh}`
      );

      if (response.data.error) {
        setError(response.data.error);
        setSongs([]);
      } else {
        setSongs(response.data.playlist || []);
      }

      if (!refresh) {
        setMessages([...messages, { text: input, sender: 'user' }]);
        setInput('');
      }
    } catch (err) {
      setError('❌ Failed to fetch songs. Try again.');
    } finally {
      setLoading(false);
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

        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type how you feel..."
          />
          <button onClick={() => fetchSongs(false)}>Send</button>
        </div>

        {loading && <p>⏳ Finding songs...</p>}
        {error && <p className="error">{error}</p>}

        {songs.length > 0 && (
          <div className="song-list">
            <h2>Trending {mood} Songs</h2>
            <button className="refresh-button" onClick={() => fetchSongs(true)}>🔄 Refresh</button>
            <div className="songs">
              {songs.map((song, index) => (
                <div key={index} className="song">
                  <img src={song.album_cover} alt={song.title} width="100" />
                  <p><strong>{song.title}</strong></p>
                  <p>{song.artist}</p>
                  <a href={song.spotify_url} target="_blank" rel="noopener noreferrer">🎵 Listen</a>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
