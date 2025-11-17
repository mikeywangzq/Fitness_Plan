/**
 * 浏览器通知 Hook
 * 
 * 使用 Notification API 实现消息推送功能
 * V1.1 新功能
 */
import { useState, useEffect, useCallback } from 'react';

export const useNotification = () => {
  const [permission, setPermission] = useState('default');
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    // 检查浏览器是否支持通知API
    if ('Notification' in window) {
      setIsSupported(true);
      setPermission(Notification.permission);
    }
  }, []);

  // 请求通知权限
  const requestPermission = useCallback(async () => {
    if (!isSupported) {
      return false;
    }

    try {
      const result = await Notification.requestPermission();
      setPermission(result);
      return result === 'granted';
    } catch (error) {
      console.error('请求通知权限失败:', error);
      return false;
    }
  }, [isSupported]);

  // 发送通知
  const sendNotification = useCallback((title, options = {}) => {
    if (!isSupported) {
      console.warn('浏览器不支持通知功能');
      return null;
    }

    if (permission !== 'granted') {
      console.warn('未获得通知权限');
      return null;
    }

    try {
      const notification = new Notification(title, {
        icon: '/icon-192x192.png',
        badge: '/icon-96x96.png',
        vibrate: [200, 100, 200],
        ...options
      });

      // 点击通知时的处理
      notification.onclick = () => {
        window.focus();
        notification.close();
        if (options.onClick) {
          options.onClick();
        }
      };

      return notification;
    } catch (error) {
      console.error('发送通知失败:', error);
      return null;
    }
  }, [isSupported, permission]);

  // 发送训练提醒
  const sendWorkoutReminder = useCallback((workoutName) => {
    return sendNotification('🏋️ 训练提醒', {
      body: `该进行${workoutName}训练了！保持规律，成就更好的自己`,
      tag: 'workout-reminder',
      requireInteraction: false
    });
  }, [sendNotification]);

  // 发送饮食提醒
  const sendMealReminder = useCallback((mealType) => {
    return sendNotification('🍽️ 饮食提醒', {
      body: `该吃${mealType}了！营养均衡很重要`,
      tag: 'meal-reminder',
      requireInteraction: false
    });
  }, [sendNotification]);

  // 发送喝水提醒
  const sendWaterReminder = useCallback(() => {
    return sendNotification('💧 喝水提醒', {
      body: '该补充水分了！保持充足的水分摄入',
      tag: 'water-reminder',
      requireInteraction: false
    });
  }, [sendNotification]);

  return {
    isSupported,
    permission,
    requestPermission,
    sendNotification,
    sendWorkoutReminder,
    sendMealReminder,
    sendWaterReminder
  };
};
