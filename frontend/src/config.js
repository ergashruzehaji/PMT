// API Configuration
// Current Railway deployment URL
const RAILWAY_URL = 'https://pmt-production-a984.up.railway.app';

// Check multiple possible Railway URLs (backup)
const POSSIBLE_URLS = [
  'https://pmt-production-a984.up.railway.app',
  'https://pmt-production-8f79794d.up.railway.app',
  'https://web-production-8f79794d.up.railway.app', 
  'https://lavish-presence-production.up.railway.app',
  'https://pmt-production.up.railway.app'
];

// For development, you can also use localhost
const DEV_URL = 'http://localhost:8000';

// Export the base URL - Use Railway for production, localhost for development
export const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? RAILWAY_URL  // Use current Railway URL for production
  : DEV_URL;  // Use localhost for development

