import client from './client.ts';
import type { TokenResponse, User } from '../types/index.ts';

export async function register(email: string, password: string, full_name: string, role = 'contractor'): Promise<TokenResponse> {
  const res = await client.post('/auth/register', { email, password, full_name, role });
  return res.data;
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const res = await client.post('/auth/login', { email, password });
  return res.data;
}

export async function getMe(): Promise<User> {
  const res = await client.get('/auth/me');
  return res.data;
}
