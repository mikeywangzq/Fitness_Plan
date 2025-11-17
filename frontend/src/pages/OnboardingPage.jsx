/**
 * 用户引导页面
 *
 * 收集用户的健身目标、身体数据和训练偏好
 * 实现 FR-1: 用户引导与目标设定
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../styles/Onboarding.css';

export default function OnboardingPage() {
  const navigate = useNavigate();
  const { completeOnboarding } = useAuth();

  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    // 基本信息
    age: '',
    gender: '',
    height: '',
    weight: '',

    // 健身目标
    fitness_goal: '',
    experience_level: 'BEGINNER',
    equipment_access: 'BODYWEIGHT',
    training_frequency: 3,

    // 目标设定
    target_weight: '',
    target_body_fat: '',
    goal_timeframe: '',

    // 饮食信息
    dietary_restrictions: '',
    allergies: ''
  });

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleNext = () => {
    setStep(step + 1);
    setError('');
  };

  const handleBack = () => {
    setStep(step - 1);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // 转换数字字段
      const submitData = {
        ...formData,
        age: formData.age ? parseInt(formData.age) : null,
        height: formData.height ? parseFloat(formData.height) : null,
        weight: formData.weight ? parseFloat(formData.weight) : null,
        target_weight: formData.target_weight ? parseFloat(formData.target_weight) : null,
        target_body_fat: formData.target_body_fat ? parseFloat(formData.target_body_fat) : null,
        goal_timeframe: formData.goal_timeframe ? parseInt(formData.goal_timeframe) : null,
        training_frequency: parseInt(formData.training_frequency)
      };

      await completeOnboarding(submitData);
      navigate('/'); // 完成引导后跳转到主页
    } catch (err) {
      console.error('引导流程失败:', err);
      setError(err.response?.data?.detail || '保存失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="onboarding-container">
      <div className="onboarding-card">
        <div className="onboarding-progress">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${(step / 4) * 100}%` }}
            />
          </div>
          <div className="progress-text">步骤 {step} / 4</div>
        </div>

        {error && (
          <div className="onboarding-error">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* 步骤 1: 基本信息 */}
          {step === 1 && (
            <div className="onboarding-step">
              <h2>基本信息</h2>
              <p className="step-description">让我们了解一下你的基本情况</p>

              <div className="form-grid">
                <div className="form-group">
                  <label>年龄</label>
                  <input
                    type="number"
                    name="age"
                    value={formData.age}
                    onChange={handleChange}
                    placeholder="25"
                    min="10"
                    max="100"
                  />
                </div>

                <div className="form-group">
                  <label>性别</label>
                  <select name="gender" value={formData.gender} onChange={handleChange}>
                    <option value="">请选择</option>
                    <option value="male">男</option>
                    <option value="female">女</option>
                    <option value="other">其他</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>身高 (cm)</label>
                  <input
                    type="number"
                    name="height"
                    value={formData.height}
                    onChange={handleChange}
                    placeholder="175"
                    min="100"
                    max="250"
                    step="0.1"
                  />
                </div>

                <div className="form-group">
                  <label>体重 (kg)</label>
                  <input
                    type="number"
                    name="weight"
                    value={formData.weight}
                    onChange={handleChange}
                    placeholder="70"
                    min="30"
                    max="300"
                    step="0.1"
                  />
                </div>
              </div>

              <div className="button-group">
                <button type="button" onClick={handleNext} className="btn-primary">
                  下一步
                </button>
              </div>
            </div>
          )}

          {/* 步骤 2: 健身目标 */}
          {step === 2 && (
            <div className="onboarding-step">
              <h2>健身目标</h2>
              <p className="step-description">告诉我们你的健身目标和经验水平</p>

              <div className="form-group">
                <label>健身目标</label>
                <select name="fitness_goal" value={formData.fitness_goal} onChange={handleChange}>
                  <option value="">请选择</option>
                  <option value="LOSE_WEIGHT">减脂</option>
                  <option value="GAIN_MUSCLE">增肌</option>
                  <option value="MAINTAIN">保持</option>
                  <option value="ATHLETIC">运动表现</option>
                  <option value="GENERAL_FITNESS">综合健身</option>
                </select>
              </div>

              <div className="form-group">
                <label>经验水平</label>
                <select name="experience_level" value={formData.experience_level} onChange={handleChange}>
                  <option value="BEGINNER">新手（0-6个月）</option>
                  <option value="INTERMEDIATE">中级（6个月-2年）</option>
                  <option value="ADVANCED">高级（2年以上）</option>
                </select>
              </div>

              <div className="form-group">
                <label>设备条件</label>
                <select name="equipment_access" value={formData.equipment_access} onChange={handleChange}>
                  <option value="BODYWEIGHT">徒手（无器械）</option>
                  <option value="BASIC">基础器械（哑铃、弹力带）</option>
                  <option value="HOME_GYM">家庭健身房</option>
                  <option value="FULL_GYM">专业健身房</option>
                </select>
              </div>

              <div className="form-group">
                <label>每周训练次数</label>
                <input
                  type="range"
                  name="training_frequency"
                  value={formData.training_frequency}
                  onChange={handleChange}
                  min="1"
                  max="7"
                />
                <div className="range-value">{formData.training_frequency} 次/周</div>
              </div>

              <div className="button-group">
                <button type="button" onClick={handleBack} className="btn-secondary">
                  上一步
                </button>
                <button type="button" onClick={handleNext} className="btn-primary">
                  下一步
                </button>
              </div>
            </div>
          )}

          {/* 步骤 3: 目标设定 */}
          {step === 3 && (
            <div className="onboarding-step">
              <h2>目标设定</h2>
              <p className="step-description">设定你的具体目标（可选）</p>

              <div className="form-group">
                <label>目标体重 (kg)</label>
                <input
                  type="number"
                  name="target_weight"
                  value={formData.target_weight}
                  onChange={handleChange}
                  placeholder="65"
                  step="0.1"
                />
              </div>

              <div className="form-group">
                <label>目标体脂率 (%)</label>
                <input
                  type="number"
                  name="target_body_fat"
                  value={formData.target_body_fat}
                  onChange={handleChange}
                  placeholder="15"
                  step="0.1"
                />
              </div>

              <div className="form-group">
                <label>目标时间（周）</label>
                <input
                  type="number"
                  name="goal_timeframe"
                  value={formData.goal_timeframe}
                  onChange={handleChange}
                  placeholder="12"
                />
              </div>

              <div className="button-group">
                <button type="button" onClick={handleBack} className="btn-secondary">
                  上一步
                </button>
                <button type="button" onClick={handleNext} className="btn-primary">
                  下一步
                </button>
              </div>
            </div>
          )}

          {/* 步骤 4: 饮食信息 */}
          {step === 4 && (
            <div className="onboarding-step">
              <h2>饮食信息</h2>
              <p className="step-description">告诉我们你的饮食偏好（可选）</p>

              <div className="form-group">
                <label>饮食限制</label>
                <textarea
                  name="dietary_restrictions"
                  value={formData.dietary_restrictions}
                  onChange={handleChange}
                  placeholder="例如：素食、低碳水、生酮等"
                  rows="3"
                />
              </div>

              <div className="form-group">
                <label>过敏信息</label>
                <textarea
                  name="allergies"
                  value={formData.allergies}
                  onChange={handleChange}
                  placeholder="例如：乳糖不耐受、坚果过敏等"
                  rows="3"
                />
              </div>

              <div className="button-group">
                <button type="button" onClick={handleBack} className="btn-secondary">
                  上一步
                </button>
                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? '保存中...' : '完成'}
                </button>
              </div>
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
