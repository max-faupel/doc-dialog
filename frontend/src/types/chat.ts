import type { ApiErrorKind } from '@/api/client'
import type { Source } from '@/types/api'

export type ChatMessage =
  | { id: number; role: 'user'; text: string }
  | { id: number; role: 'assistant'; status: 'loading'; question: string }
  | { id: number; role: 'assistant'; status: 'done'; text: string; sources: Source[] }
  | {
      id: number
      role: 'assistant'
      status: 'error'
      text: string
      errorKind: ApiErrorKind
      question: string
    }
