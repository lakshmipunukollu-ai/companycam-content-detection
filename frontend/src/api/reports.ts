import client from './client.ts';
import type { ProjectReport } from '../types/index.ts';

export async function getProjectReport(projectId: string): Promise<ProjectReport> {
  const res = await client.get(`/reports/${projectId}`);
  return res.data;
}
