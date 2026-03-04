import { useState, useEffect } from 'react';
import TaskForm from '../components/TaskForm';
import TaskList from '../components/TaskList';
import TaskDetail from '../components/TaskDetail';
import SearchFilter from '../components/SearchFilter';
import ProfileSettings from '../components/ProfileSettings';
import { getProfile, logout } from '../services/authApi';

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [selectedTask, setSelectedTask] = useState(null);
  const [showProfile, setShowProfile] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadProfile() {
      try {
        const profile = await getProfile();
        setUser(profile);
      } catch {
        // Profile failed — clear stale tokens and reload to show login
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.reload();
        return;
      } finally {
        setLoading(false);
      }
    }
    loadProfile();
  }, []);

  function handleTaskCreated() {
    setRefreshTrigger(prev => prev + 1);
  }

  function handleTaskUpdated() {
    setSelectedTask(null);
    setRefreshTrigger(prev => prev + 1);
  }

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Todo Chatbot</h1>
        <div className="user-info">
          {user && <span>Welcome, {user.username}!</span>}
          <button className="btn-secondary" onClick={() => setShowProfile(true)}>Settings</button>
          <button className="btn-secondary" onClick={logout}>Logout</button>
        </div>
      </header>

      <main className="dashboard-content">
        {showProfile && (
          <ProfileSettings onClose={() => setShowProfile(false)} />
        )}

        {selectedTask ? (
          <TaskDetail
            task={selectedTask}
            onClose={() => setSelectedTask(null)}
            onUpdated={handleTaskUpdated}
          />
        ) : (
          <>
            <TaskForm onTaskCreated={handleTaskCreated} />
            <SearchFilter onFilterChange={() => setRefreshTrigger(prev => prev + 1)} />
            <TaskList
              refreshTrigger={refreshTrigger}
              onSelectTask={setSelectedTask}
            />
          </>
        )}
      </main>
    </div>
  );
}
