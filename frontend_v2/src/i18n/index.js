import { createI18n } from 'vue-i18n';
import en from './locales/en.json';
import vi from './locales/vi.json';

// Define messages
const messages = {
  en,
  vi
};

// Create i18n instance
const i18n = createI18n({
  legacy: false, // Use Composition API
  locale: 'vi', // Default locale
  fallbackLocale: 'en', // Fallback locale
  messages,
});

export default i18n;
