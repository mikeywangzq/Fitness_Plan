/**
 * i18n 国际化配置
 *
 * 支持语言：中文(zh)、英语(en)、日语(ja)、韩语(ko)
 * V1.1 新功能
 */
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import zh from './locales/zh.json';
import en from './locales/en.json';
import ja from './locales/ja.json';
import ko from './locales/ko.json';

i18n
  // 使用浏览器语言检测
  .use(LanguageDetector)
  // 使用 react-i18next
  .use(initReactI18next)
  // 初始化配置
  .init({
    resources: {
      zh: { translation: zh },
      en: { translation: en },
      ja: { translation: ja },
      ko: { translation: ko }
    },
    fallbackLng: 'zh', // 默认语言
    lng: 'zh', // 初始语言

    detection: {
      // 语言检测顺序
      order: ['localStorage', 'navigator', 'htmlTag'],
      // localStorage 键名
      lookupLocalStorage: 'i18nextLng',
      // 缓存用户语言
      caches: ['localStorage'],
    },

    interpolation: {
      escapeValue: false // React 已经处理了 XSS
    },

    react: {
      useSuspense: false // 禁用 Suspense，避免加载闪烁
    }
  });

export default i18n;
