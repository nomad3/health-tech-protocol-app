import { describe, it, expect, beforeEach, vi } from 'vitest';
import { authService } from './authService';
import api from './api';
import { UserRole } from '../types/auth';
import type { AuthResponse } from '../types/auth';

// Mock the api module
vi.mock('./api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

describe('Auth Service', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  describe('register', () => {
    it('calls the register endpoint with correct data', async () => {
      const mockResponse: AuthResponse = {
        access_token: 'access-token',
        refresh_token: 'refresh-token',
        token_type: 'bearer',
        user: {
          id: 1,
          email: 'test@example.com',
          role: UserRole.PATIENT,
          is_active: true,
          created_at: '2024-01-01',
        },
      };

      (api.post as any).mockResolvedValue({ data: mockResponse });

      const registerData = {
        email: 'test@example.com',
        password: 'password123',
        role: UserRole.PATIENT,
      };

      const result = await authService.register(registerData);

      expect(api.post).toHaveBeenCalledWith('/api/v1/auth/register', registerData);
      expect(result).toEqual(mockResponse);
    });
  });

  describe('login', () => {
    it('calls the login endpoint with correct credentials', async () => {
      const mockResponse: AuthResponse = {
        access_token: 'access-token',
        refresh_token: 'refresh-token',
        token_type: 'bearer',
        user: {
          id: 1,
          email: 'test@example.com',
          role: UserRole.PATIENT,
          is_active: true,
          created_at: '2024-01-01',
        },
      };

      (api.post as any).mockResolvedValue({ data: mockResponse });

      const loginData = {
        email: 'test@example.com',
        password: 'password123',
      };

      const result = await authService.login(loginData);

      expect(api.post).toHaveBeenCalledWith('/api/v1/auth/login', loginData);
      expect(result).toEqual(mockResponse);
    });
  });

  describe('logout', () => {
    it('clears localStorage after logout', async () => {
      localStorage.setItem('access_token', 'token');
      localStorage.setItem('refresh_token', 'refresh');
      localStorage.setItem('user', JSON.stringify({ id: 1, email: 'test@example.com' }));

      (api.post as any).mockResolvedValue({});

      await authService.logout();

      expect(localStorage.getItem('access_token')).toBeNull();
      expect(localStorage.getItem('refresh_token')).toBeNull();
      expect(localStorage.getItem('user')).toBeNull();
    });

    it('clears localStorage even if API call fails', async () => {
      localStorage.setItem('access_token', 'token');
      (api.post as any).mockRejectedValue(new Error('Network error'));

      try {
        await authService.logout();
      } catch (error) {
        // Expected to catch error
      }

      expect(localStorage.getItem('access_token')).toBeNull();
    });
  });

  describe('saveAuthData', () => {
    it('saves auth data to localStorage', () => {
      const authData: AuthResponse = {
        access_token: 'access-token',
        refresh_token: 'refresh-token',
        token_type: 'bearer',
        user: {
          id: 1,
          email: 'test@example.com',
          role: UserRole.PATIENT,
          is_active: true,
          created_at: '2024-01-01',
        },
      };

      authService.saveAuthData(authData);

      expect(localStorage.getItem('access_token')).toBe('access-token');
      expect(localStorage.getItem('refresh_token')).toBe('refresh-token');
      expect(JSON.parse(localStorage.getItem('user')!)).toEqual(authData.user);
    });
  });

  describe('getSavedUser', () => {
    it('returns user from localStorage', () => {
      const user = {
        id: 1,
        email: 'test@example.com',
        role: UserRole.PATIENT,
        is_active: true,
        created_at: '2024-01-01',
      };

      localStorage.setItem('user', JSON.stringify(user));

      const result = authService.getSavedUser();
      expect(result).toEqual(user);
    });

    it('returns null when no user in localStorage', () => {
      const result = authService.getSavedUser();
      expect(result).toBeNull();
    });

    it('returns null when localStorage data is invalid', () => {
      localStorage.setItem('user', 'invalid-json');
      const result = authService.getSavedUser();
      expect(result).toBeNull();
    });
  });

  describe('isAuthenticated', () => {
    it('returns true when access token exists', () => {
      localStorage.setItem('access_token', 'token');
      expect(authService.isAuthenticated()).toBe(true);
    });

    it('returns false when no access token exists', () => {
      expect(authService.isAuthenticated()).toBe(false);
    });
  });
});
