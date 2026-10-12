import type { AskRequest, AskResponse, HealthResponse } from '@/types/api'

const BASE_URL = '/api'

// network: Backend nicht erreichbar, llm: Backend erreichbar, aber LLM-Aufruf fehlgeschlagen
export type ApiErrorKind = 'network' | 'llm' | 'validation' | 'unknown'

export class ApiError extends Error {
  readonly kind: ApiErrorKind
  readonly status?: number

  constructor(kind: ApiErrorKind, message: string, status?: number) {
    super(message)
    this.name = 'ApiError'
    this.kind = kind
    this.status = status
  }
}

const NETWORK_MESSAGE =
  'Das Backend ist nicht erreichbar. Läuft „uvicorn app:app“ in backend/ auf Port 8000?'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...init?.headers },
    })
  } catch {
    throw new ApiError('network', NETWORK_MESSAGE)
  }

  // Antworten, die nicht vom Backend stammen (z. B. Vite-Proxy-Fehler), haben kein JSON
  const body: unknown = await res.json().catch(() => null)

  if (res.ok && body !== null) return body as T

  const detail = (body as { detail?: unknown } | null)?.detail

  if (detail === undefined) {
    // Ohne FastAPI-"detail" kam die Antwort nicht vom Backend: Proxy-Fehler, Backend aus
    if (res.status >= 500 || res.status === 0)
      throw new ApiError('network', NETWORK_MESSAGE, res.status)
    throw new ApiError(
      'unknown',
      `Unerwartete Antwort vom Server (HTTP ${res.status}).`,
      res.status,
    )
  }

  if (res.status === 422) {
    throw new ApiError(
      'validation',
      'Die Frage ist ungültig. Sie muss mindestens 3 Zeichen lang sein.',
      422,
    )
  }
  if (res.status === 502) {
    throw new ApiError(
      'llm',
      `Das Backend läuft, aber das Sprachmodell antwortet nicht. Läuft Ollama bzw. ist der Cloud-Zugang korrekt konfiguriert?\n${String(detail)}`,
      502,
    )
  }
  throw new ApiError(
    'unknown',
    `Fehler vom Server (HTTP ${res.status}): ${String(detail)}`,
    res.status,
  )
}

export function ask(payload: AskRequest): Promise<AskResponse> {
  return request<AskResponse>('/ask', { method: 'POST', body: JSON.stringify(payload) })
}

export function health(): Promise<HealthResponse> {
  return request<HealthResponse>('/health')
}
