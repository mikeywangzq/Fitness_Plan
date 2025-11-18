import { useState } from 'react'
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../contexts/AuthContext'
import LanguageSwitcher from './LanguageSwitcher'
import '../styles/layout.css'

function Layout() {
  const { t } = useTranslation()
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const navigation = [
    { name: t('nav.chat'), path: '/', icon: '💬' },
    { name: t('nav.dashboard'), path: '/dashboard', icon: '📊' },
    { name: t('nav.workout'), path: '/workout', icon: '🏋️' },
    { name: t('nav.nutrition'), path: '/nutrition', icon: '🥗' },
    { name: t('nav.progress'), path: '/progress', icon: '📈' },
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
        <h1 className="mobile-title">💪 {t('common.appName')}</h1>
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
          <h1>💪 {t('common.appName')}</h1>
          <LanguageSwitcher />
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
            {t('nav.logout')}
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
