// Spiegelt die Pydantic-Modelle aus backend/app.py

export interface AskRequest {
  question: string
  top_k?: number
}

export interface Source {
  source: string
  page: number | null
  distance: number
  text: string
}

export interface AskResponse {
  answer: string
  sources: Source[]
}

export interface HealthResponse {
  chunks_im_index: number
  llm_base_url: string
  chat_model: string
  embed_model: string
}
