/**
 * API service for backend communication.
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('auth_token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Authentication APIs
export const authApi = {
  login: () => {
    window.location.href = `${API_BASE_URL}/auth/google/login`;
  },

  logout: async () => {
    await api.post('/auth/logout');
    localStorage.removeItem('auth_token');
  },

  setToken: (token) => {
    localStorage.setItem('auth_token', token);
  },

  getToken: () => {
    return localStorage.getItem('auth_token');
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('auth_token');
  },
};

// Recording APIs
export const recordingApi = {
  /**
   * Create a new recording session
   */
  createRecording: async () => {
    const response = await api.post('/recordings/');
    return response.data;
  },

  /**
   * List all recordings for the current user
   */
  listRecordings: async () => {
    const response = await api.get('/recordings/');
    return response.data.recordings;
  },

  /**
   * Get a specific recording
   */
  getRecording: async (recordingId) => {
    const response = await api.get(`/recordings/${recordingId}`);
    return response.data;
  },

  /**
   * Upload an audio chunk
   */
  uploadChunk: async (recordingId, chunkIndex, audioBlob, durationSeconds) => {
    const formData = new FormData();
    formData.append('chunk_index', chunkIndex);
    formData.append('audio_chunk', audioBlob, `chunk_${chunkIndex}.webm`);
    if (durationSeconds !== null) {
      formData.append('duration_seconds', durationSeconds);
    }

    const response = await api.post(
      `/recordings/${recordingId}/chunks`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  /**
   * Pause a recording
   */
  pauseRecording: async (recordingId) => {
    const response = await api.patch(`/recordings/${recordingId}/pause`);
    return response.data;
  },

  /**
   * Finish a recording and trigger transcription
   */
  finishRecording: async (recordingId) => {
    const response = await api.post(`/recordings/${recordingId}/finish`);
    return response.data;
  },

  /**
   * Add or update notes for a recording
   */
  addNotes: async (recordingId, notes) => {
    const response = await api.patch(`/recordings/${recordingId}/notes`, { notes });
    return response.data;
  },

  /**
   * Delete a recording
   */
  deleteRecording: async (recordingId) => {
    await api.delete(`/recordings/${recordingId}`);
  },
};

export default api;
