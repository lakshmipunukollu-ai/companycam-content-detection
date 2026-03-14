import client from './client.ts';
import type { Correction, CorrectionCreate } from '../types/index.ts';

export async function createCorrection(photoId: string, data: CorrectionCreate): Promise<Correction> {
  const res = await client.post(`/photos/${photoId}/corrections`, data);
  return res.data;
}

export async function getCorrections(photoId: string): Promise<Correction[]> {
  const res = await client.get(`/photos/${photoId}/corrections`);
  return res.data;
}
