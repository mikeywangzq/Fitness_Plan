import { useState } from 'react'
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import '../styles/layout.css'

function Layout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const navigation = [
    { name: '聊天助手', path: '/', icon: '💬' },
    { name: '仪表盘', path: '/dashboard', icon: '📊' },
    { name: '训练计划', path: '/workout', icon: '🏋️' },
    { name: '营养追踪', path: '/nutrition', icon: '🥗' },
    { name: '进度分析', path: '/progress', icon: '📈' },
  ]

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen)
  }

  const closeSidebar = () => {
    setSidebarOpen(false)
  }

  return (
    <div className="app-container">
      {/* 移动端顶部栏 */}
      <div className="mobile-header">
        <button className="menu-toggle" onClick={toggleSidebar} aria-label="Toggle menu">
          <span className="hamburger"></span>
          <span className="hamburger"></span>
          <span className="hamburger"></span>
        </button>
        <h1 className="mobile-title">💪 Fitness Planner</h1>
        <div className="mobile-user-avatar">
          {user?.username?.charAt(0).toUpperCase() || 'U'}
        </div>
      </div>

      {/* 遮罩层 */}
      {sidebarOpen && (
        <div className="sidebar-overlay" onClick={closeSidebar}></div>
      )}

      <nav className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
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
                onClick={closeSidebar}
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-text">{item.name}</span>
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
