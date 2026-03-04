import { useState, useEffect } from 'react';
import Login from '../components/Login';
import Register from '../components/Register';
import Dashboard from './Dashboard';
import { isAuthenticated } from '../services/authApi';

export default function Home() {
  const [authed, setAuthed] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  useEffect(() => {
    setAuthed(isAuthenticated());
  }, []);

  if (authed) return <Dashboard />;

  if (showRegister) {
    return (
      <div className="auth-container">
        <Register
          onRegistered={() => setShowRegister(false)}
          onSwitchToLogin={() => setShowRegister(false)}
        />
      </div>
    );
  }

  return (
    <div className="auth-container">
      <Login
        onLogin={() => setAuthed(true)}
        onSwitchToRegister={() => setShowRegister(true)}
      />
    </div>
  );
}
