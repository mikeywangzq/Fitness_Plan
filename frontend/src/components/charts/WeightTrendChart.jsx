/**
 * 体重趋势图表
 * 
 * 显示用户体重随时间的变化趋势
 * V1.1 数据可视化功能
 */
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';

export default function WeightTrendChart({ data }) {
  // 示例数据格式
  // data = [
  //   { date: '2025-01-01', weight: 75, targetWeight: 70 },
  //   { date: '2025-01-08', weight: 74.5, targetWeight: 70 },
  //   ...
  // ]

  if (!data || data.length === 0) {
    return (
      <div className="chart-placeholder">
        <p>暂无体重数据</p>
        <p className="placeholder-hint">开始记录你的体重数据以查看趋势图</p>
      </div>
    );
  }

  // 格式化数据
  const formattedData = data.map(item => ({
    ...item,
    date: item.date ? format(new Date(item.date), 'MM/dd') : ''
  }));

  return (
    <div className="chart-container">
      <h3 className="chart-title">体重趋势</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={formattedData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis 
            dataKey="date" 
            stroke="#64748b"
            style={{ fontSize: '0.875rem' }}
          />
          <YAxis 
            stroke="#64748b"
            style={{ fontSize: '0.875rem' }}
            domain={['dataMin - 2', 'dataMax + 2']}
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
          <Line 
            type="monotone" 
            dataKey="weight" 
            stroke="#667eea" 
            strokeWidth={2}
            name="实际体重 (kg)"
            dot={{ fill: '#667eea', r: 4 }}
            activeDot={{ r: 6 }}
          />
          {formattedData.some(d => d.targetWeight) && (
            <Line 
              type="monotone" 
              dataKey="targetWeight" 
              stroke="#10b981" 
              strokeWidth={2}
              strokeDasharray="5 5"
              name="目标体重 (kg)"
              dot={false}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
