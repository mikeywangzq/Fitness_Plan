/**
 * 仪表盘页面
 * 
 * 展示用户健身数据概览和提醒设置
 * V1.1 增强
 */
import ReminderSettings from '../components/ReminderSettings';
import '../styles/dashboard.css';

function DashboardPage() {
  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h2>仪表盘</h2>
        <p>快速查看你的健身数据和设置提醒</p>
      </div>

      <div className="dashboard-content">
        {/* 快速统计卡片 */}
        <div className="dashboard-grid">
          <div className="dashboard-card">
            <div className="card-icon">💪</div>
            <h3>本周训练</h3>
            <div className="card-value">3<span className="card-unit">/5 次</span></div>
            <div className="card-progress">
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: '60%' }}></div>
              </div>
            </div>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">🍽️</div>
            <h3>今日营养</h3>
            <div className="card-value">1500<span className="card-unit">/2500 kcal</span></div>
            <div className="card-progress">
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: '60%' }}></div>
              </div>
            </div>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">⚖️</div>
            <h3>体重变化</h3>
            <div className="card-value">-0.5<span className="card-unit">kg</span></div>
            <div className="card-change positive">本周 ↓</div>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">🔥</div>
            <h3>训练强度</h3>
            <div className="card-value">中等</div>
            <div className="card-change">保持良好</div>
          </div>
        </div>

        {/* 提醒设置 */}
        <div className="dashboard-section">
          <ReminderSettings />
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;
