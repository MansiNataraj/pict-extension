import { useState, useEffect } from 'react';
import { getLanguages } from '../services/api';

const DEFAULT_LANGUAGES = [
  { code: 'hi', name: 'Hindi', native: 'हिन्दी', direction: 'ltr', font_class: 'font-devanagari' },
  { code: 'ta', name: 'Tamil', native: 'தமிழ்', direction: 'ltr', font_class: 'font-tamil' },
  { code: 'kn', name: 'Kannada', native: 'ಕನ್ನಡ', direction: 'ltr', font_class: 'font-kannada' },
  { code: 'ar', name: 'Arabic', native: 'العربية', direction: 'rtl', font_class: 'font-arabic' },
];

export function useLanguage() {
  const [languages, setLanguages] = useState(DEFAULT_LANGUAGES);
  const [selectedLang, setSelectedLang] = useState('hi');

  useEffect(() => {
    getLanguages()
      .then((res) => {
        if (res.data && res.data.length > 0) {
          setLanguages(res.data);
        }
      })
      .catch((err) => {
        console.warn('Backend offline, using fallback languages:', err.message);
      });
  }, []);

  const currentLanguage = languages.find((l) => l.code === selectedLang) || languages[0];
  const isRTL = currentLanguage?.direction === 'rtl';

  return {
    languages,
    selectedLang,
    setSelectedLang,
    currentLanguage,
    isRTL,
  };
}