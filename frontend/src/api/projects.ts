import client from './client.ts';
import type { Project, ProjectCreate } from '../types/index.ts';

export async function listProjects(status?: string): Promise<Project[]> {
  const params: Record<string, string> = {};
  if (status) params.status = status;
  const res = await client.get('/projects', { params });
  return res.data;
}

export async function getProject(id: string): Promise<Project> {
  const res = await client.get(`/projects/${id}`);
  return res.data;
}

export async function createProject(data: ProjectCreate): Promise<Project> {
  const res = await client.post('/projects', data);
  return res.data;
}

export async function updateProject(id: string, data: Partial<ProjectCreate & { status: string }>): Promise<Project> {
  const res = await client.put(`/projects/${id}`, data);
  return res.data;
}

export async function deleteProject(id: string): Promise<void> {
  await client.delete(`/projects/${id}`);
}
