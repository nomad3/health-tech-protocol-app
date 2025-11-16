import { describe, it, expect, vi, beforeEach } from 'vitest';
import protocolService from './protocolService';
import { api } from './api';
import { TherapyType, EvidenceLevel } from '../types/protocol';

vi.mock('./api');

describe('protocolService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getProtocols', () => {
    it('should fetch protocols with filters', async () => {
      const mockResponse = {
        data: {
          protocols: [
            {
              id: 1,
              name: 'Test Protocol',
              therapy_type: TherapyType.PSILOCYBIN,
              evidence_level: EvidenceLevel.PHASE_3,
            },
          ],
          total: 1,
          page: 1,
          page_size: 20,
        },
      };

      vi.mocked(api.get).mockResolvedValue(mockResponse);

      const result = await protocolService.getProtocols(
        { therapy_type: TherapyType.PSILOCYBIN },
        1,
        20
      );

      expect(api.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/protocols')
      );
      expect(result.protocols).toHaveLength(1);
      expect(result.total).toBe(1);
    });
  });

  describe('getProtocol', () => {
    it('should fetch a single protocol by ID', async () => {
      const mockProtocol = {
        id: 1,
        name: 'Test Protocol',
        therapy_type: TherapyType.PSILOCYBIN,
      };

      vi.mocked(api.get).mockResolvedValue({ data: mockProtocol });

      const result = await protocolService.getProtocol(1);

      expect(api.get).toHaveBeenCalledWith('/api/v1/protocols/1');
      expect(result.id).toBe(1);
      expect(result.name).toBe('Test Protocol');
    });
  });

  describe('createProtocol', () => {
    it('should create a new protocol', async () => {
      const newProtocol = {
        name: 'New Protocol',
        therapy_type: TherapyType.MDMA,
        version: '1.0',
      };

      vi.mocked(api.post).mockResolvedValue({ data: { ...newProtocol, id: 1 } });

      const result = await protocolService.createProtocol(newProtocol);

      expect(api.post).toHaveBeenCalledWith('/api/v1/admin/protocols', newProtocol);
      expect(result.id).toBe(1);
    });
  });

  describe('updateProtocol', () => {
    it('should update an existing protocol', async () => {
      const updates = { name: 'Updated Protocol' };

      vi.mocked(api.put).mockResolvedValue({ data: { id: 1, ...updates } });

      const result = await protocolService.updateProtocol(1, updates);

      expect(api.put).toHaveBeenCalledWith('/api/v1/admin/protocols/1', updates);
      expect(result.name).toBe('Updated Protocol');
    });
  });

  describe('deleteProtocol', () => {
    it('should delete a protocol', async () => {
      vi.mocked(api.delete).mockResolvedValue({ data: null });

      await protocolService.deleteProtocol(1);

      expect(api.delete).toHaveBeenCalledWith('/api/v1/admin/protocols/1');
    });
  });

  describe('searchProtocols', () => {
    it('should search protocols by query', async () => {
      const mockResults = [
        { id: 1, name: 'Protocol 1' },
        { id: 2, name: 'Protocol 2' },
      ];

      vi.mocked(api.get).mockResolvedValue({ data: mockResults });

      const result = await protocolService.searchProtocols('test query');

      expect(api.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/protocols/search')
      );
      expect(result).toHaveLength(2);
    });
  });
});
