import type {
  AuthResponse,
  LoginRequest,
  RefreshTokenRequest,
  RegisterRequest,
  User,
} from '../types/auth';
import api from './api';

const AUTH_API_BASE = '/api/v1/auth';

export const authService = {
  /**
   * Register a new user
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>(`${AUTH_API_BASE}/register`, data);
    return response.data;
  },

  /**
   * Login with email and password
   */
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>(`${AUTH_API_BASE}/login`, data);
    return response.data;
  },

  /**
   * Refresh access token
   */
  async refreshToken(data: RefreshTokenRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>(`${AUTH_API_BASE}/refresh`, data);
    return response.data;
  },

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      await api.post(`${AUTH_API_BASE}/logout`);
    } finally {
      // Clear local storage regardless of API call success
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  },

  /**
   * Get current user
   */
  async getMe(): Promise<User> {
    const response = await api.get<User>(`${AUTH_API_BASE}/me`);
    return response.data;
  },

  /**
   * Save auth data to localStorage
   */
  saveAuthData(data: { access_token: string; refresh_token: string }): void {
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
  },

  /**
   * Get saved user from localStorage
   */
  getSavedUser(): User | null {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    try {
      return JSON.parse(userStr) as User;
    } catch {
      return null;
    }
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },
};

export default authService;
