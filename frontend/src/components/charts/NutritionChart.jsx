/**
 * 营养摄入图表
 * 
 * 显示每日营养摄入（蛋白质、碳水、脂肪）
 * V1.1 数据可视化功能
 */
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const COLORS = {
  protein: '#667eea',
  carbs: '#10b981',
  fat: '#f59e0b'
};

export default function NutritionChart({ data }) {
  // 示例数据格式
  // data = {
  //   protein: 150,
  //   carbs: 250,
  //   fat: 60
  // }

  if (!data || (!data.protein && !data.carbs && !data.fat)) {
    return (
      <div className="chart-placeholder">
        <p>暂无营养数据</p>
        <p className="placeholder-hint">开始记录你的饮食以查看营养分布</p>
      </div>
    );
  }

  const chartData = [
    { name: '蛋白质', value: data.protein || 0, color: COLORS.protein },
    { name: '碳水化合物', value: data.carbs || 0, color: COLORS.carbs },
    { name: '脂肪', value: data.fat || 0, color: COLORS.fat }
  ];

  const total = chartData.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className="chart-container">
      <h3 className="chart-title">今日营养摄入</h3>
      <div className="nutrition-summary">
        <div className="nutrition-item">
          <span className="nutrition-label" style={{ color: COLORS.protein }}>蛋白质</span>
          <span className="nutrition-value">{data.protein}g</span>
        </div>
        <div className="nutrition-item">
          <span className="nutrition-label" style={{ color: COLORS.carbs }}>碳水</span>
          <span className="nutrition-value">{data.carbs}g</span>
        </div>
        <div className="nutrition-item">
          <span className="nutrition-label" style={{ color: COLORS.fat }}>脂肪</span>
          <span className="nutrition-value">{data.fat}g</span>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip 
            formatter={(value) => `${value}g`}
            contentStyle={{ 
              backgroundColor: 'white', 
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              padding: '12px'
            }}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="nutrition-total">
        总热量：约 {Math.round(data.protein * 4 + data.carbs * 4 + data.fat * 9)} kcal
      </div>
    </div>
  );
}
