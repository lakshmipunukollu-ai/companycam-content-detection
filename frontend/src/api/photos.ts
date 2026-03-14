import client from './client.ts';
import type { Photo, PhotoAnalysisResult } from '../types/index.ts';

export async function uploadPhoto(file: File, projectId: string, photoType: string): Promise<Photo> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('project_id', projectId);
  formData.append('photo_type', photoType);
  const res = await client.post('/photos/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

export async function analyzePhoto(photoId: string): Promise<PhotoAnalysisResult> {
  const formData = new FormData();
  formData.append('photo_id', photoId);
  const res = await client.post('/photos/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

export async function getPhoto(id: string): Promise<Photo> {
  const res = await client.get(`/photos/${id}`);
  return res.data;
}

export async function getPhotoResults(id: string): Promise<PhotoAnalysisResult> {
  const res = await client.get(`/photos/${id}/results`);
  return res.data;
}

export async function listPhotos(projectId?: string, status?: string): Promise<Photo[]> {
  const params: Record<string, string> = {};
  if (projectId) params.project_id = projectId;
  if (status) params.status = status;
  const res = await client.get('/photos', { params });
  return res.data;
}

export async function deletePhoto(id: string): Promise<void> {
  await client.delete(`/photos/${id}`);
}
