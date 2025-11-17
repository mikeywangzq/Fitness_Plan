import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import '../styles/layout.css'

function Layout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const navigation = [
    { name: '聊天助手', path: '/' },
    { name: '仪表盘', path: '/dashboard' },
    { name: '训练计划', path: '/workout' },
    { name: '营养追踪', path: '/nutrition' },
    { name: '进度分析', path: '/progress' },
  ]

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="app-container">
      <nav className="sidebar">
        <div className="sidebar-header">
          <h1>💪 Fitness Planner</h1>
          <p>AI健身助手</p>
        </div>

        {/* 用户信息 */}
        {user && (
          <div className="user-info">
            <div className="user-avatar">
              {user.username?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="user-details">
              <div className="user-name">{user.username}</div>
              <div className="user-email">{user.email}</div>
            </div>
          </div>
        )}

        <ul className="nav-menu">
          {navigation.map((item) => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={location.pathname === item.path ? 'active' : ''}
              >
                {item.name}
              </Link>
            </li>
          ))}
        </ul>

        <div className="sidebar-footer">
          <button onClick={handleLogout} className="logout-button">
            登出
          </button>
          <p>v1.1.0</p>
        </div>
      </nav>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout
