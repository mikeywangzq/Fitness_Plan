/**
 * 语音输入按钮组件
 * 
 * 提供语音识别功能的按钮界面
 * V1.1 新功能
 */
import { useEffect } from 'react';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';
import '../styles/VoiceInput.css';

export default function VoiceInputButton({ onTranscript, className }) {
  const {
    isSupported,
    isListening,
    transcript,
    error,
    startListening,
    stopListening,
    resetTranscript,
  } = useSpeechRecognition();

  // 当识别完成时，将结果传递给父组件
  useEffect(() => {
    if (transcript && !isListening) {
      onTranscript(transcript);
      resetTranscript();
    }
  }, [transcript, isListening, onTranscript, resetTranscript]);

  // 如果不支持，不显示按钮
  if (!isSupported) {
    return null;
  }

  const handleClick = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  return (
    <div className={`voice-input-container ${className || ''}`}>
      <button
        type="button"
        className={`voice-input-button ${isListening ? 'listening' : ''}`}
        onClick={handleClick}
        title={isListening ? '点击停止' : '点击开始语音输入'}
        aria-label={isListening ? '停止语音输入' : '开始语音输入'}
      >
        {isListening ? (
          <>
            <span className="mic-icon recording">🎙️</span>
            <span className="pulse-ring"></span>
            <span className="pulse-ring-2"></span>
          </>
        ) : (
          <span className="mic-icon">🎤</span>
        )}
      </button>

      {isListening && (
        <div className="listening-indicator">
          <span className="listening-text">正在听...</span>
          {transcript && (
            <span className="interim-transcript">{transcript}</span>
          )}
        </div>
      )}

      {error && (
        <div className="voice-error">
          {error}
        </div>
      )}
    </div>
  );
}
