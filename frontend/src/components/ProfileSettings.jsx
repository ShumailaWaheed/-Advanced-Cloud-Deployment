import { useState, useEffect } from 'react';
import { getProfile, updateProfile } from '../services/authApi';

export default function ProfileSettings({ onClose }) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const profile = await getProfile();
        setUsername(profile.username);
        setEmail(profile.email);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  async function handleSave(e) {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSaving(true);
    try {
      await updateProfile({ username, email });
      setSuccess('Profile updated successfully.');
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <div className="loading">Loading profile...</div>;

  return (
    <div className="profile-settings">
      <div className="detail-header">
        <h3>Profile Settings</h3>
        <button className="btn-close" onClick={onClose}>Close</button>
      </div>
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}
      <form onSubmit={handleSave}>
        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input id="username" value={username} onChange={e => setUsername(e.target.value)} minLength={3} maxLength={50} required />
        </div>
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input id="email" type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        </div>
        <button type="submit" disabled={saving}>{saving ? 'Saving...' : 'Save Changes'}</button>
      </form>
    </div>
  );
}
