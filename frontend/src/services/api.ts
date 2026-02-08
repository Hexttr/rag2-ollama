import axios from 'axios'
import type { Document, Chat, Message, QueryRequest } from '../types'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Health
export const healthApi = {
  check: () => api.get('/api/health'),
  checkOllama: () => api.get('/api/health/ollama'),
}

// Documents
export const documentsApi = {
  getAll: () => api.get<Document[]>('/api/documents'),
  getById: (id: number) => api.get<Document>(`/api/documents/${id}`),
  upload: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<{ id: number; filename: string; status: string; message: string }>(
      '/api/documents/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
  },
  getStatus: (id: number) => api.get<{ id: number; status: string; error_message: string | null }>(
    `/api/documents/${id}/status`
  ),
  delete: (id: number) => api.delete(`/api/documents/${id}`),
}

// Chats
export const chatsApi = {
  create: (documentId?: number, title?: string) =>
    api.post<Chat>('/api/chats', { document_id: documentId, title }),
  getAll: (documentId?: number) =>
    api.get<Chat[]>('/api/chats', { params: documentId ? { document_id: documentId } : {} }),
  getById: (id: number) => api.get<Chat>(`/api/chats/${id}`),
  getMessages: (id: number) => api.get<Message[]>(`/api/chats/${id}/messages`),
  query: (chatId: number, query: string, documentId?: number) =>
    api.post<Message>(`/api/chats/${chatId}/query`, {
      query,
      document_id: documentId,
    } as QueryRequest),
  delete: (id: number) => api.delete(`/api/chats/${id}`),
}

export default api

