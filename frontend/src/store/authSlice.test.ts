import { describe, it, expect, beforeEach } from 'vitest';
import authReducer, { setUser, clearAuth, clearError } from './authSlice';
import { UserRole } from '../types/auth';
import type { AuthState } from '../types/auth';

describe('Auth Slice', () => {
  let initialState: AuthState;

  beforeEach(() => {
    initialState = {
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      loading: false,
      error: null,
    };
  });

  it('should return the initial state', () => {
    expect(authReducer(undefined, { type: 'unknown' })).toEqual({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      loading: false,
      error: null,
    });
  });

  describe('setUser', () => {
    it('should set the user and mark as authenticated', () => {
      const user = {
        id: 1,
        email: 'test@example.com',
        role: UserRole.PATIENT,
        is_active: true,
        created_at: '2024-01-01',
      };

      const state = authReducer(initialState, setUser(user));

      expect(state.user).toEqual(user);
      expect(state.isAuthenticated).toBe(true);
    });
  });

  describe('clearAuth', () => {
    it('should clear all auth state', () => {
      const authenticatedState: AuthState = {
        user: {
          id: 1,
          email: 'test@example.com',
          role: UserRole.PATIENT,
          is_active: true,
          created_at: '2024-01-01',
        },
        token: 'access-token',
        refreshToken: 'refresh-token',
        isAuthenticated: true,
        loading: false,
        error: null,
      };

      const state = authReducer(authenticatedState, clearAuth());

      expect(state.user).toBeNull();
      expect(state.token).toBeNull();
      expect(state.refreshToken).toBeNull();
      expect(state.isAuthenticated).toBe(false);
      expect(state.error).toBeNull();
    });
  });

  describe('clearError', () => {
    it('should clear the error state', () => {
      const stateWithError: AuthState = {
        ...initialState,
        error: 'Login failed',
      };

      const state = authReducer(stateWithError, clearError());

      expect(state.error).toBeNull();
    });
  });
});
