/**
 * 提醒设置组件
 * 
 * 允许用户设置训练和饮食提醒
 * V1.1 新功能
 */
import { useState, useEffect } from 'react';
import { useNotification } from '../hooks/useNotification';
import '../styles/Reminders.css';

export default function ReminderSettings() {
  const {
    isSupported,
    permission,
    requestPermission,
    sendWorkoutReminder,
    sendMealReminder,
    sendWaterReminder
  } = useNotification();

  const [reminders, setReminders] = useState({
    workoutEnabled: false,
    workoutTime: '18:00',
    workoutDays: [1, 3, 5], // 周一、三、五
    
    breakfastEnabled: false,
    breakfastTime: '08:00',
    
    lunchEnabled: false,
    lunchTime: '12:00',
    
    dinnerEnabled: false,
    dinnerTime: '18:30',
    
    waterEnabled: false,
    waterInterval: 60, // 每60分钟提醒一次
  });

  const [testMessage, setTestMessage] = useState('');

  // 从 localStorage 加载设置
  useEffect(() => {
    const saved = localStorage.getItem('reminderSettings');
    if (saved) {
      try {
        setReminders(JSON.parse(saved));
      } catch (e) {
        console.error('加载提醒设置失败:', e);
      }
    }
  }, []);

  // 保存设置到 localStorage
  const saveSettings = (newSettings) => {
    setReminders(newSettings);
    localStorage.setItem('reminderSettings', JSON.stringify(newSettings));
  };

  // 处理权限请求
  const handleEnableNotifications = async () => {
    const granted = await requestPermission();
    if (granted) {
      setTestMessage('通知权限已授予！');
      setTimeout(() => setTestMessage(''), 3000);
    } else {
      setTestMessage('通知权限被拒绝');
      setTimeout(() => setTestMessage(''), 3000);
    }
  };

  // 测试通知
  const handleTestNotification = () => {
    sendWorkoutReminder('力量训练');
    setTestMessage('已发送测试通知');
    setTimeout(() => setTestMessage(''), 3000);
  };

  const weekDays = [
    { value: 0, label: '日' },
    { value: 1, label: '一' },
    { value: 2, label: '二' },
    { value: 3, label: '三' },
    { value: 4, label: '四' },
    { value: 5, label: '五' },
    { value: 6, label: '六' },
  ];

  const toggleWorkoutDay = (day) => {
    const newDays = reminders.workoutDays.includes(day)
      ? reminders.workoutDays.filter(d => d !== day)
      : [...reminders.workoutDays, day].sort();
    saveSettings({ ...reminders, workoutDays: newDays });
  };

  if (!isSupported) {
    return (
      <div className="reminders-container">
        <div className="not-supported">
          <p>您的浏览器不支持通知功能</p>
          <p className="hint">请使用 Chrome、Firefox 或 Edge 浏览器</p>
        </div>
      </div>
    );
  }

  return (
    <div className="reminders-container">
      <div className="reminders-header">
        <h3>提醒设置</h3>
        <p>设置训练和饮食提醒，养成良好习惯</p>
      </div>

      {/* 权限状态 */}
      <div className={`permission-status ${permission}`}>
        {permission === 'default' && (
          <>
            <p>通知权限未授予</p>
            <button onClick={handleEnableNotifications} className="btn-primary">
              启用通知
            </button>
          </>
        )}
        {permission === 'granted' && (
          <>
            <p className="success">✅ 通知权限已授予</p>
            <button onClick={handleTestNotification} className="btn-secondary">
              发送测试通知
            </button>
          </>
        )}
        {permission === 'denied' && (
          <p className="error">❌ 通知权限被拒绝，请在浏览器设置中允许通知</p>
        )}
        {testMessage && <p className="test-message">{testMessage}</p>}
      </div>

      {permission === 'granted' && (
        <>
          {/* 训练提醒 */}
          <div className="reminder-section">
            <div className="reminder-header">
              <div className="reminder-title">
                <span className="reminder-icon">🏋️</span>
                <span>训练提醒</span>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={reminders.workoutEnabled}
                  onChange={(e) => saveSettings({ ...reminders, workoutEnabled: e.target.checked })}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>

            {reminders.workoutEnabled && (
              <div className="reminder-details">
                <div className="form-group">
                  <label>提醒时间</label>
                  <input
                    type="time"
                    value={reminders.workoutTime}
                    onChange={(e) => saveSettings({ ...reminders, workoutTime: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>提醒日期</label>
                  <div className="week-days">
                    {weekDays.map(day => (
                      <button
                        key={day.value}
                        className={`day-btn ${reminders.workoutDays.includes(day.value) ? 'active' : ''}`}
                        onClick={() => toggleWorkoutDay(day.value)}
                      >
                        {day.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* 早餐提醒 */}
          <div className="reminder-section">
            <div className="reminder-header">
              <div className="reminder-title">
                <span className="reminder-icon">🍳</span>
                <span>早餐提醒</span>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={reminders.breakfastEnabled}
                  onChange={(e) => saveSettings({ ...reminders, breakfastEnabled: e.target.checked })}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
            {reminders.breakfastEnabled && (
              <div className="reminder-details">
                <div className="form-group">
                  <label>提醒时间</label>
                  <input
                    type="time"
                    value={reminders.breakfastTime}
                    onChange={(e) => saveSettings({ ...reminders, breakfastTime: e.target.value })}
                  />
                </div>
              </div>
            )}
          </div>

          {/* 午餐提醒 */}
          <div className="reminder-section">
            <div className="reminder-header">
              <div className="reminder-title">
                <span className="reminder-icon">🍱</span>
                <span>午餐提醒</span>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={reminders.lunchEnabled}
                  onChange={(e) => saveSettings({ ...reminders, lunchEnabled: e.target.checked })}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
            {reminders.lunchEnabled && (
              <div className="reminder-details">
                <div className="form-group">
                  <label>提醒时间</label>
                  <input
                    type="time"
                    value={reminders.lunchTime}
                    onChange={(e) => saveSettings({ ...reminders, lunchTime: e.target.value })}
                  />
                </div>
              </div>
            )}
          </div>

          {/* 晚餐提醒 */}
          <div className="reminder-section">
            <div className="reminder-header">
              <div className="reminder-title">
                <span className="reminder-icon">🍽️</span>
                <span>晚餐提醒</span>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={reminders.dinnerEnabled}
                  onChange={(e) => saveSettings({ ...reminders, dinnerEnabled: e.target.checked })}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
            {reminders.dinnerEnabled && (
              <div className="reminder-details">
                <div className="form-group">
                  <label>提醒时间</label>
                  <input
                    type="time"
                    value={reminders.dinnerTime}
                    onChange={(e) => saveSettings({ ...reminders, dinnerTime: e.target.value })}
                  />
                </div>
              </div>
            )}
          </div>

          {/* 喝水提醒 */}
          <div className="reminder-section">
            <div className="reminder-header">
              <div className="reminder-title">
                <span className="reminder-icon">💧</span>
                <span>喝水提醒</span>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={reminders.waterEnabled}
                  onChange={(e) => saveSettings({ ...reminders, waterEnabled: e.target.checked })}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
            {reminders.waterEnabled && (
              <div className="reminder-details">
                <div className="form-group">
                  <label>提醒间隔（分钟）</label>
                  <input
                    type="number"
                    value={reminders.waterInterval}
                    onChange={(e) => saveSettings({ ...reminders, waterInterval: parseInt(e.target.value) })}
                    min="30"
                    max="180"
                    step="15"
                  />
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
