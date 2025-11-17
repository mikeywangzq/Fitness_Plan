function DashboardPage() {
  return (
    <div className="dashboard-page">
      <h2>仪表盘</h2>
      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h3>本周训练</h3>
          <p>已完成 3/5 次</p>
        </div>
        <div className="dashboard-card">
          <h3>今日营养</h3>
          <p>热量: 1500/2500 kcal</p>
        </div>
        <div className="dashboard-card">
          <h3>体重变化</h3>
          <p>+0.5 kg 本周</p>
        </div>
        <div className="dashboard-card">
          <h3>训练强度</h3>
          <p>中等强度</p>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
