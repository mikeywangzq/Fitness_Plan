/**
 * 认证服务
 *
 * 处理用户登录、注册、token 管理等功能
 */
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * 用户注册
 * @param {Object} userData - 注册信息
 * @param {string} userData.email - 邮箱
 * @param {string} userData.username - 用户名
 * @param {string} userData.password - 密码
 * @param {string} userData.full_name - 全名（可选）
 * @returns {Promise<Object>} 包含 token 和用户信息
 */
export const register = async (userData) => {
  const response = await axios.post(`${API_URL}/api/users/register`, userData);
  if (response.data.access_token) {
    localStorage.setItem('token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
  }
  return response.data;
};

/**
 * 用户登录
 * @param {Object} credentials - 登录凭据
 * @param {string} credentials.email - 邮箱
 * @param {string} credentials.password - 密码
 * @returns {Promise<Object>} 包含 token 和用户信息
 */
export const login = async (credentials) => {
  const response = await axios.post(`${API_URL}/api/users/login`, credentials);
  if (response.data.access_token) {
    localStorage.setItem('token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
  }
  return response.data;
};

/**
 * 用户登出
 */
export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

/**
 * 获取当前用户信息
 * @returns {Promise<Object>} 用户信息
 */
export const getCurrentUser = async () => {
  const token = localStorage.getItem('token');
  if (!token) {
    throw new Error('未登录');
  }

  const response = await axios.get(`${API_URL}/api/users/me`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

  localStorage.setItem('user', JSON.stringify(response.data));
  return response.data;
};

/**
 * 更新用户信息
 * @param {Object} userData - 要更新的用户信息
 * @returns {Promise<Object>} 更新后的用户信息
 */
export const updateUser = async (userData) => {
  const token = localStorage.getItem('token');
  if (!token) {
    throw new Error('未登录');
  }

  const response = await axios.put(`${API_URL}/api/users/me`, userData, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

  localStorage.setItem('user', JSON.stringify(response.data));
  return response.data;
};

/**
 * 完成用户引导流程
 * @param {Object} onboardingData - 引导数据
 * @returns {Promise<Object>} 更新后的用户信息
 */
export const completeOnboarding = async (onboardingData) => {
  const token = localStorage.getItem('token');
  if (!token) {
    throw new Error('未登录');
  }

  const response = await axios.post(`${API_URL}/api/users/me/onboarding`, onboardingData, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

  localStorage.setItem('user', JSON.stringify(response.data));
  return response.data;
};

/**
 * 获取存储的 token
 * @returns {string|null} JWT token
 */
export const getToken = () => {
  return localStorage.getItem('token');
};

/**
 * 获取存储的用户信息
 * @returns {Object|null} 用户信息
 */
export const getStoredUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

/**
 * 检查用户是否已认证
 * @returns {boolean} 是否已认证
 */
export const isAuthenticated = () => {
  const token = getToken();
  if (!token) return false;

  // 简单检查 token 是否过期（解析 JWT payload）
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp * 1000 > Date.now();
  } catch (e) {
    return false;
  }
};

// Axios 拦截器：自动在请求头中添加 token
axios.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Axios 拦截器：处理 401 错误（token 过期）
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Token 过期或无效，清除本地存储并跳转到登录页
      logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
