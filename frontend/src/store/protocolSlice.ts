import type { PayloadAction } from '@reduxjs/toolkit';
import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import protocolService from '../services/protocolService';
import type { Protocol, ProtocolFilters } from '../types/protocol';

interface ProtocolState {
  protocols: Protocol[];
  selectedProtocol: Protocol | null;
  filters: ProtocolFilters;
  loading: boolean;
  error: string | null;
  total: number;
  page: number;
  pageSize: number;
}

const initialState: ProtocolState = {
  protocols: [],
  selectedProtocol: null,
  filters: {},
  loading: false,
  error: null,
  total: 0,
  page: 1,
  pageSize: 20,
};

// Async thunks
export const fetchProtocols = createAsyncThunk(
  'protocol/fetchProtocols',
  async ({ filters, page, pageSize }: { filters?: ProtocolFilters; page?: number; pageSize?: number }) => {
    const response = await protocolService.getProtocols(filters, page, pageSize);
    return response;
  }
);

export const fetchProtocol = createAsyncThunk('protocol/fetchProtocol', async (id: number) => {
  const response = await protocolService.getProtocol(id);
  return response;
});

export const createProtocol = createAsyncThunk('protocol/createProtocol', async (protocol: Partial<Protocol>) => {
  const response = await protocolService.createProtocol(protocol);
  return response;
});

export const updateProtocol = createAsyncThunk(
  'protocol/updateProtocol',
  async ({ id, updates }: { id: number; updates: Partial<Protocol> }) => {
    const response = await protocolService.updateProtocol(id, updates);
    return response;
  }
);

export const deleteProtocol = createAsyncThunk('protocol/deleteProtocol', async (id: number) => {
  await protocolService.deleteProtocol(id);
  return id;
});

export const searchProtocols = createAsyncThunk('protocol/searchProtocols', async (query: string) => {
  const response = await protocolService.searchProtocols(query);
  return response;
});

const protocolSlice = createSlice({
  name: 'protocol',
  initialState,
  reducers: {
    setFilters: (state, action: PayloadAction<ProtocolFilters>) => {
      state.filters = action.payload;
    },
    clearFilters: (state) => {
      state.filters = {};
    },
    setSelectedProtocol: (state, action: PayloadAction<Protocol | null>) => {
      state.selectedProtocol = action.payload;
    },
    setPage: (state, action: PayloadAction<number>) => {
      state.page = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch protocols
    builder
      .addCase(fetchProtocols.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProtocols.fulfilled, (state, action) => {
        state.loading = false;
        state.protocols = action.payload.items;
        state.total = action.payload.total;
        state.page = action.payload.page;
        state.pageSize = action.payload.size;
      })
      .addCase(fetchProtocols.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch protocols';
      });

    // Fetch single protocol
    builder
      .addCase(fetchProtocol.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProtocol.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedProtocol = action.payload;
      })
      .addCase(fetchProtocol.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch protocol';
      });

    // Create protocol
    builder
      .addCase(createProtocol.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createProtocol.fulfilled, (state, action) => {
        state.loading = false;
        state.protocols.push(action.payload);
        state.selectedProtocol = action.payload;
      })
      .addCase(createProtocol.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to create protocol';
      });

    // Update protocol
    builder
      .addCase(updateProtocol.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateProtocol.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.protocols.findIndex((p) => p.id === action.payload.id);
        if (index !== -1) {
          state.protocols[index] = action.payload;
        }
        if (state.selectedProtocol?.id === action.payload.id) {
          state.selectedProtocol = action.payload;
        }
      })
      .addCase(updateProtocol.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to update protocol';
      });

    // Delete protocol
    builder
      .addCase(deleteProtocol.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteProtocol.fulfilled, (state, action) => {
        state.loading = false;
        state.protocols = state.protocols.filter((p) => p.id !== action.payload);
        if (state.selectedProtocol?.id === action.payload) {
          state.selectedProtocol = null;
        }
      })
      .addCase(deleteProtocol.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to delete protocol';
      });

    // Search protocols
    builder
      .addCase(searchProtocols.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(searchProtocols.fulfilled, (state, action) => {
        state.loading = false;
        state.protocols = action.payload;
        state.total = action.payload.length;
      })
      .addCase(searchProtocols.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to search protocols';
      });
  },
});

export const { setFilters, clearFilters, setSelectedProtocol, setPage, clearError } = protocolSlice.actions;

export default protocolSlice.reducer;
