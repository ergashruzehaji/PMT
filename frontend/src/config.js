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

// Auto-detect best API URL based on environment and availability
const getApiUrl = () => {
  // If running locally (localhost), prefer local API if available
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return DEV_URL;
  }
  
  // Otherwise use Railway for production
  return RAILWAY_URL;
};

// Export the base URL - Use smart detection for best sync experience
export const API_BASE_URL = getApiUrl();

