/**
 * Domain Management Redux Slice
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { DomainService } from '../../services/DomainService';

export interface SSLStatus {
  is_valid: boolean;
  expires_in: number;
  issuer?: string;
  subject?: string;
  not_valid_after?: string;
  checked_at?: string;
}

export interface Domain {
  id: number;
  name: string;
  is_active: boolean;
  alert_threshold_days: number;
  created_at: string;
  updated_at: string;
  ssl_status?: SSLStatus;
}

interface DomainState {
  domains: Domain[];
  selectedDomain: Domain | null;
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

const initialState: DomainState = {
  domains: [],
  selectedDomain: null,
  isLoading: false,
  error: null,
  lastUpdated: null,
};

// Async thunks
export const fetchDomains = createAsyncThunk(
  'domains/fetchDomains',
  async () => {
    const response = await DomainService.getDomains();
    return response;
  }
);

export const addDomain = createAsyncThunk(
  'domains/addDomain',
  async (domainData: { name: string; alert_threshold_days?: number }) => {
    const response = await DomainService.addDomain(domainData);
    return response;
  }
);

export const updateDomain = createAsyncThunk(
  'domains/updateDomain',
  async ({ id, domainData }: { id: number; domainData: Partial<Domain> }) => {
    const response = await DomainService.updateDomain(id, domainData);
    return response;
  }
);

export const deleteDomain = createAsyncThunk(
  'domains/deleteDomain',
  async (id: number) => {
    await DomainService.deleteDomain(id);
    return id;
  }
);

export const checkSSLStatus = createAsyncThunk(
  'domains/checkSSLStatus',
  async (id: number) => {
    const response = await DomainService.checkSSLStatus(id);
    return { id, ssl_status: response };
  }
);

export const refreshDomainStatus = createAsyncThunk(
  'domains/refreshDomainStatus',
  async (id: number) => {
    const response = await DomainService.refreshDomainStatus(id);
    return { id, ssl_status: response };
  }
);

// Domain slice
const domainSlice = createSlice({
  name: 'domains',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setSelectedDomain: (state, action: PayloadAction<Domain | null>) => {
      state.selectedDomain = action.payload;
    },
    updateDomainInList: (state, action: PayloadAction<{ id: number; updates: Partial<Domain> }>) => {
      const index = state.domains.findIndex(domain => domain.id === action.payload.id);
      if (index !== -1) {
        state.domains[index] = { ...state.domains[index], ...action.payload.updates };
      }
    },
    removeDomainFromList: (state, action: PayloadAction<number>) => {
      state.domains = state.domains.filter(domain => domain.id !== action.payload);
    },
  },
  extraReducers: (builder) => {
    // Fetch domains
    builder
      .addCase(fetchDomains.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchDomains.fulfilled, (state, action) => {
        state.isLoading = false;
        state.domains = action.payload;
        state.lastUpdated = new Date().toISOString();
        state.error = null;
      })
      .addCase(fetchDomains.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to fetch domains';
      });

    // Add domain
    builder
      .addCase(addDomain.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(addDomain.fulfilled, (state, action) => {
        state.isLoading = false;
        state.domains.push(action.payload);
        state.error = null;
      })
      .addCase(addDomain.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to add domain';
      });

    // Update domain
    builder
      .addCase(updateDomain.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updateDomain.fulfilled, (state, action) => {
        state.isLoading = false;
        const index = state.domains.findIndex(domain => domain.id === action.payload.id);
        if (index !== -1) {
          state.domains[index] = action.payload;
        }
        state.error = null;
      })
      .addCase(updateDomain.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to update domain';
      });

    // Delete domain
    builder
      .addCase(deleteDomain.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(deleteDomain.fulfilled, (state, action) => {
        state.isLoading = false;
        state.domains = state.domains.filter(domain => domain.id !== action.payload);
        if (state.selectedDomain?.id === action.payload) {
          state.selectedDomain = null;
        }
        state.error = null;
      })
      .addCase(deleteDomain.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to delete domain';
      });

    // Check SSL status
    builder
      .addCase(checkSSLStatus.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(checkSSLStatus.fulfilled, (state, action) => {
        state.isLoading = false;
        const index = state.domains.findIndex(domain => domain.id === action.payload.id);
        if (index !== -1) {
          state.domains[index].ssl_status = action.payload.ssl_status;
        }
        state.error = null;
      })
      .addCase(checkSSLStatus.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to check SSL status';
      });

    // Refresh domain status
    builder
      .addCase(refreshDomainStatus.fulfilled, (state, action) => {
        const index = state.domains.findIndex(domain => domain.id === action.payload.id);
        if (index !== -1) {
          state.domains[index].ssl_status = action.payload.ssl_status;
        }
      });
  },
});

export const { clearError, setSelectedDomain, updateDomainInList, removeDomainFromList } = domainSlice.actions;
export default domainSlice.reducer;
