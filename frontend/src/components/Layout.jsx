import { Outlet, Link, useLocation } from 'react-router-dom'
import '../styles/layout.css'

function Layout() {
  const location = useLocation()

  const navigation = [
    { name: '聊天助手', path: '/' },
    { name: '仪表盘', path: '/dashboard' },
    { name: '训练计划', path: '/workout' },
    { name: '营养追踪', path: '/nutrition' },
    { name: '进度分析', path: '/progress' },
  ]

  return (
    <div className="app-container">
      <nav className="sidebar">
        <div className="sidebar-header">
          <h1>💪 Fitness Planner</h1>
          <p>AI健身助手</p>
        </div>

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
          <p>v1.0.0</p>
        </div>
      </nav>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout
