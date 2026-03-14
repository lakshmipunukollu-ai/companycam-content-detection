import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.tsx';

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();

  if (!isAuthenticated) return null;

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">CompanyCam Detection</Link>
      </div>
      <div className="navbar-links">
        <Link to="/">Projects</Link>
      </div>
      <div className="navbar-user">
        <span className="user-info">{user?.full_name} ({user?.role})</span>
        <button className="btn btn-sm btn-secondary" onClick={logout}>Logout</button>
      </div>
    </nav>
  );
}
