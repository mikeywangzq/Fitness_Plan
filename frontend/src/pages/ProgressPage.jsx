/**
 * 进度分析页面
 * 
 * 展示用户的健身进度数据和可视化图表
 * V1.1 数据可视化增强
 */
import { useState } from 'react';
import WeightTrendChart from '../components/charts/WeightTrendChart';
import WorkoutVolumeChart from '../components/charts/WorkoutVolumeChart';
import NutritionChart from '../components/charts/NutritionChart';
import '../styles/Charts.css';
import '../styles/progress.css';

function ProgressPage() {
  // 模拟数据 - 实际应用中从 API 获取
  const [weightData] = useState([
    { date: '2025-01-01', weight: 75, targetWeight: 70 },
    { date: '2025-01-08', weight: 74.5, targetWeight: 70 },
    { date: '2025-01-15', weight: 74, targetWeight: 70 },
    { date: '2025-01-22', weight: 73.5, targetWeight: 70 },
    { date: '2025-01-29', weight: 73, targetWeight: 70 },
    { date: '2025-02-05', weight: 72.5, targetWeight: 70 },
  ]);

  const [workoutData] = useState([
    { week: '第1周', sessions: 4, totalSets: 80 },
    { week: '第2周', sessions: 5, totalSets: 95 },
    { week: '第3周', sessions: 4, totalSets: 85 },
    { week: '第4周', sessions: 5, totalSets: 100 },
    { week: '第5周', sessions: 5, totalSets: 105 },
  ]);

  const [nutritionData] = useState({
    protein: 150,
    carbs: 250,
    fat: 60
  });

  const stats = {
    currentWeight: 72.5,
    weightChange: -2.5,
    totalWorkouts: 23,
    workoutStreak: 5,
    totalSets: 465,
    avgCalories: 2200
  };

  return (
    <div className="progress-page">
      <div className="progress-header">
        <h2>进度分析</h2>
        <p>追踪你的健身成就和进步</p>
      </div>

      <div className="progress-content">
        {/* 统计卡片 */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">⚖️</div>
            <div className="stat-label">当前体重</div>
            <div className="stat-value">{stats.currentWeight} kg</div>
            <div className={`stat-change ${stats.weightChange < 0 ? 'positive' : 'negative'}`}>
              {stats.weightChange > 0 ? '+' : ''}{stats.weightChange} kg
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">💪</div>
            <div className="stat-label">训练次数</div>
            <div className="stat-value">{stats.totalWorkouts}</div>
            <div className="stat-change positive">本月已完成</div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🔥</div>
            <div className="stat-label">连续训练</div>
            <div className="stat-value">{stats.workoutStreak} 天</div>
            <div className="stat-change positive">保持良好习惯</div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">📈</div>
            <div className="stat-label">总训练组数</div>
            <div className="stat-value">{stats.totalSets}</div>
            <div className="stat-change positive">不断突破</div>
          </div>
        </div>

        {/* 图表区域 */}
        <div className="charts-section">
          <div className="chart-row">
            <div className="chart-col-full">
              <WeightTrendChart data={weightData} />
            </div>
          </div>

          <div className="chart-row">
            <div className="chart-col">
              <WorkoutVolumeChart data={workoutData} />
            </div>
            <div className="chart-col">
              <NutritionChart data={nutritionData} />
            </div>
          </div>
        </div>

        {/* 成就徽章 */}
        <div className="achievements-section">
          <h3 className="section-title">成就徽章</h3>
          <div className="achievements-grid">
            <div className="achievement-card unlocked">
              <div className="achievement-icon">🏆</div>
              <div className="achievement-name">新手上路</div>
              <div className="achievement-desc">完成第一次训练</div>
            </div>
            <div className="achievement-card unlocked">
              <div className="achievement-icon">⭐</div>
              <div className="achievement-name">坚持者</div>
              <div className="achievement-desc">连续训练 5 天</div>
            </div>
            <div className="achievement-card unlocked">
              <div className="achievement-icon">💯</div>
              <div className="achievement-name">百组达人</div>
              <div className="achievement-desc">单周完成 100 组训练</div>
            </div>
            <div className="achievement-card locked">
              <div className="achievement-icon">🎖️</div>
              <div className="achievement-name">月度冠军</div>
              <div className="achievement-desc">单月训练 20 次</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProgressPage;
