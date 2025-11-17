/**
 * 训练量统计图表
 * 
 * 显示每周训练量统计（训练次数、总组数、总重量等）
 * V1.1 数据可视化功能
 */
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function WorkoutVolumeChart({ data }) {
  // 示例数据格式
  // data = [
  //   { week: 'Week 1', sessions: 4, totalSets: 80, totalVolume: 12000 },
  //   { week: 'Week 2', sessions: 5, totalSets: 95, totalVolume: 14500 },
  //   ...
  // ]

  if (!data || data.length === 0) {
    return (
      <div className="chart-placeholder">
        <p>暂无训练数据</p>
        <p className="placeholder-hint">开始记录你的训练数据以查看统计图</p>
      </div>
    );
  }

  return (
    <div className="chart-container">
      <h3 className="chart-title">训练量统计</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis 
            dataKey="week" 
            stroke="#64748b"
            style={{ fontSize: '0.875rem' }}
          />
          <YAxis 
            stroke="#64748b"
            style={{ fontSize: '0.875rem' }}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'white', 
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              padding: '12px'
            }}
          />
          <Legend 
            wrapperStyle={{ fontSize: '0.875rem' }}
          />
          <Bar 
            dataKey="sessions" 
            fill="#667eea" 
            name="训练次数"
            radius={[8, 8, 0, 0]}
          />
          <Bar 
            dataKey="totalSets" 
            fill="#10b981" 
            name="总组数"
            radius={[8, 8, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
