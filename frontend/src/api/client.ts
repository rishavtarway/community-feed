/**
 * Axios API client configured for the Django backend.
 */

import axios from 'axios';

const apiClient = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

export default apiClient;
