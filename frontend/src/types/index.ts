// API Types

export interface Document {
  id: number
  filename: string
  status: 'uploading' | 'indexing' | 'ready' | 'error'
  created_at: string
  index_path?: string | null
}

export interface Chat {
  id: number
  document_id: number | null
  title: string | null
  created_at: string
}

export interface Message {
  id: number
  chat_id: number
  role: 'user' | 'assistant'
  content: string
  sources?: Source[] | null
  created_at: string
}

export interface Source {
  title: string
  node_id: string
  pages: string
}

export interface QueryRequest {
  query: string
  document_id?: number | null
}

export interface WebSocketMessage {
  type: 'status_update' | 'ping' | 'pong'
  status?: 'indexing' | 'ready' | 'error'
  message?: string
  index_path?: string
}




