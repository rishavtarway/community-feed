/**
 * Axios API client configured for the Django backend.
 * Uses VITE_API_URL env var on Vercel, falls back to localhost for local dev.
 */

import axios from 'axios';

// Use environment variable for production (Vercel), fallback to proxy for local dev
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const apiClient = axios.create({
    baseURL: `${API_BASE_URL}/api`,
    headers: {
        'Content-Type': 'application/json',
    },
});

export default apiClient;
