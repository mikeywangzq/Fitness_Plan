/**
 * 语言切换组件
 *
 * 支持切换中文、英文、日文、韩文
 * V1.1 新功能
 */
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import '../styles/LanguageSwitcher.css';

const languages = [
  { code: 'zh', name: '中文', flag: '🇨🇳' },
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'ja', name: '日本語', flag: '🇯🇵' },
  { code: 'ko', name: '한국어', flag: '🇰🇷' }
];

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);

  const currentLanguage = languages.find(lang => lang.code === i18n.language) || languages[0];

  const handleLanguageChange = (languageCode) => {
    i18n.changeLanguage(languageCode);
    setIsOpen(false);
  };

  return (
    <div className="language-switcher">
      <button
        className="language-button"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Switch language"
      >
        <span className="language-flag">{currentLanguage.flag}</span>
        <span className="language-name">{currentLanguage.name}</span>
        <span className="language-arrow">{isOpen ? '▲' : '▼'}</span>
      </button>

      {isOpen && (
        <div className="language-dropdown">
          {languages.map((language) => (
            <button
              key={language.code}
              className={`language-option ${i18n.language === language.code ? 'active' : ''}`}
              onClick={() => handleLanguageChange(language.code)}
            >
              <span className="option-flag">{language.flag}</span>
              <span className="option-name">{language.name}</span>
              {i18n.language === language.code && (
                <span className="option-check">✓</span>
              )}
            </button>
          ))}
        </div>
      )}

      {isOpen && (
        <div
          className="language-backdrop"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
}
