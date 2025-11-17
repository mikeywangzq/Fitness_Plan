/**
 * 语音识别 Hook
 * 
 * 使用 Web Speech API 实现语音输入功能
 * V1.1 新功能
 */
import { useState, useEffect, useCallback, useRef } from 'react';

// 检查浏览器是否支持 Web Speech API
const isSpeechRecognitionSupported = () => {
  return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
};

export const useSpeechRecognition = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState(null);
  const [isSupported, setIsSupported] = useState(false);
  
  const recognitionRef = useRef(null);

  useEffect(() => {
    // 检查浏览器支持
    if (!isSpeechRecognitionSupported()) {
      setError('您的浏览器不支持语音识别功能');
      setIsSupported(false);
      return;
    }

    setIsSupported(true);

    // 创建语音识别实例
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    // 配置
    recognition.continuous = false; // 不持续识别
    recognition.interimResults = true; // 显示临时结果
    recognition.lang = 'zh-CN'; // 中文识别
    recognition.maxAlternatives = 1;

    // 识别结果处理
    recognition.onresult = (event) => {
      let finalTranscript = '';
      let interimTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }

      setTranscript(finalTranscript || interimTranscript);
    };

    // 识别开始
    recognition.onstart = () => {
      setIsListening(true);
      setError(null);
    };

    // 识别结束
    recognition.onend = () => {
      setIsListening(false);
    };

    // 错误处理
    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
      
      switch(event.error) {
        case 'no-speech':
          setError('未检测到语音，请重试');
          break;
        case 'audio-capture':
          setError('无法访问麦克风');
          break;
        case 'not-allowed':
          setError('麦克风权限被拒绝');
          break;
        case 'network':
          setError('网络错误');
          break;
        default:
          setError(`识别错误: ${event.error}`);
      }
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  // 开始识别
  const startListening = useCallback(() => {
    if (!recognitionRef.current || isListening) return;

    try {
      setTranscript('');
      setError(null);
      recognitionRef.current.start();
    } catch (err) {
      console.error('Failed to start recognition:', err);
      setError('启动识别失败');
    }
  }, [isListening]);

  // 停止识别
  const stopListening = useCallback(() => {
    if (!recognitionRef.current || !isListening) return;

    try {
      recognitionRef.current.stop();
    } catch (err) {
      console.error('Failed to stop recognition:', err);
    }
  }, [isListening]);

  // 重置
  const resetTranscript = useCallback(() => {
    setTranscript('');
    setError(null);
  }, []);

  return {
    isSupported,
    isListening,
    transcript,
    error,
    startListening,
    stopListening,
    resetTranscript,
  };
};
