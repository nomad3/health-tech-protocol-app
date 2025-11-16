import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import protocolReducer from './protocolSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    protocol: protocolReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types
        ignoredActions: ['auth/login/fulfilled', 'auth/register/fulfilled'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
