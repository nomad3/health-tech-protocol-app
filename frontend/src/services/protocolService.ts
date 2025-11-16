import { api } from './api';
import type { Protocol, ProtocolFilters, ProtocolListResponse, ProtocolStep, SafetyCheck } from '../types/protocol';

export const protocolService = {
  /**
   * Get all protocols with optional filters
   */
  async getProtocols(filters?: ProtocolFilters, page = 1, pageSize = 20): Promise<ProtocolListResponse> {
    const params = new URLSearchParams();

    if (filters) {
      if (filters.therapy_type) params.append('therapy_type', filters.therapy_type);
      if (filters.condition) params.append('condition', filters.condition);
      if (filters.evidence_level) params.append('evidence_level', filters.evidence_level);
      if (filters.status) params.append('status', filters.status);
      if (filters.search) params.append('search', filters.search);
    }

    params.append('page', page.toString());
    params.append('page_size', pageSize.toString());

    const response = await api.get<ProtocolListResponse>(`/api/v1/protocols?${params.toString()}`);
    return response.data;
  },

  /**
   * Get a single protocol by ID
   */
  async getProtocol(id: number): Promise<Protocol> {
    const response = await api.get<Protocol>(`/api/v1/protocols/${id}`);
    return response.data;
  },

  /**
   * Create a new protocol (admin only)
   */
  async createProtocol(protocol: Partial<Protocol>): Promise<Protocol> {
    const response = await api.post<Protocol>('/api/v1/admin/protocols', protocol);
    return response.data;
  },

  /**
   * Update an existing protocol (admin only)
   */
  async updateProtocol(id: number, updates: Partial<Protocol>): Promise<Protocol> {
    const response = await api.put<Protocol>(`/api/v1/admin/protocols/${id}`, updates);
    return response.data;
  },

  /**
   * Delete a protocol (admin only)
   */
  async deleteProtocol(id: number): Promise<void> {
    await api.delete(`/api/v1/admin/protocols/${id}`);
  },

  /**
   * Add a step to a protocol (admin only)
   */
  async addProtocolStep(protocolId: number, step: Partial<ProtocolStep>): Promise<ProtocolStep> {
    const response = await api.post<ProtocolStep>(`/api/v1/admin/protocols/${protocolId}/steps`, step);
    return response.data;
  },

  /**
   * Update a protocol step (admin only)
   */
  async updateProtocolStep(protocolId: number, stepId: number, updates: Partial<ProtocolStep>): Promise<ProtocolStep> {
    const response = await api.put<ProtocolStep>(`/api/v1/admin/protocols/${protocolId}/steps/${stepId}`, updates);
    return response.data;
  },

  /**
   * Delete a protocol step (admin only)
   */
  async deleteProtocolStep(protocolId: number, stepId: number): Promise<void> {
    await api.delete(`/api/v1/admin/protocols/${protocolId}/steps/${stepId}`);
  },

  /**
   * Add a safety check to a protocol step (admin only)
   */
  async addSafetyCheck(protocolId: number, stepId: number, safetyCheck: Partial<SafetyCheck>): Promise<SafetyCheck> {
    const response = await api.post<SafetyCheck>(
      `/api/v1/admin/protocols/${protocolId}/steps/${stepId}/safety-checks`,
      safetyCheck
    );
    return response.data;
  },

  /**
   * Search protocols
   */
  async searchProtocols(query: string): Promise<Protocol[]> {
    const response = await api.get<Protocol[]>(`/api/v1/protocols/search?q=${encodeURIComponent(query)}`);
    return response.data;
  },
};

export default protocolService;
