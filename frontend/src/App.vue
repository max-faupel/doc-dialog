<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'

import { ApiError, ask, health } from '@/api/client'
import ChatInput from '@/components/ChatInput.vue'
import ChatMessage from '@/components/ChatMessage.vue'
import type { HealthResponse } from '@/types/api'
import type { ChatMessage as Message } from '@/types/chat'

const messages = ref<Message[]>([])
const status = ref<HealthResponse | 'offline' | null>(null)
const historyEl = ref<HTMLElement | null>(null)
let nextId = 1

const isLoading = computed(() =>
  messages.value.some((m) => m.role === 'assistant' && m.status === 'loading'),
)

async function scrollToBottom() {
  await nextTick()
  historyEl.value?.scrollTo({ top: historyEl.value.scrollHeight, behavior: 'smooth' })
}

async function checkHealth() {
  try {
    status.value = await health()
  } catch {
    status.value = 'offline'
  }
}

async function sendQuestion(question: string) {
  const id = nextId++
  messages.value.push({ id, role: 'assistant', status: 'loading', question })
  scrollToBottom()

  let result: Message
  try {
    const response = await ask({ question })
    result = {
      id,
      role: 'assistant',
      status: 'done',
      text: response.answer,
      sources: response.sources,
    }
    if (status.value === 'offline') checkHealth()
  } catch (error) {
    const apiError =
      error instanceof ApiError
        ? error
        : new ApiError('unknown', 'Unbekannter Fehler bei der Anfrage.')
    result = {
      id,
      role: 'assistant',
      status: 'error',
      text: apiError.message,
      errorKind: apiError.kind,
      question,
    }
    if (apiError.kind === 'network') status.value = 'offline'
  }

  const index = messages.value.findIndex((m) => m.id === id)
  if (index !== -1) messages.value[index] = result
  scrollToBottom()
}

function onSubmit(question: string) {
  messages.value.push({ id: nextId++, role: 'user', text: question })
  sendQuestion(question)
}

// Fehlgeschlagene Antwort entfernen und dieselbe Frage erneut stellen
function onRetry(id: number, question: string) {
  if (isLoading.value) return
  messages.value = messages.value.filter((m) => m.id !== id)
  sendQuestion(question)
}

onMounted(checkHealth)
</script>

<template>
  <div class="layout">
    <header class="header">
      <h1 class="header__title">doc-dialog</h1>
      <p class="header__status" :class="{ 'header__status--offline': status === 'offline' }">
        <template v-if="status === null">Verbinde …</template>
        <template v-else-if="status === 'offline'">
          Backend nicht erreichbar
          <button type="button" class="header__recheck" @click="checkHealth">Erneut prüfen</button>
        </template>
        <template v-else>
          {{ status.chunks_im_index }} Abschnitte im Index · {{ status.chat_model }}
        </template>
      </p>
    </header>

    <main ref="historyEl" class="history" aria-live="polite">
      <div class="history__inner">
        <div v-if="messages.length === 0" class="empty">
          <p class="empty__title">Stell eine Frage zu deinen Dokumenten.</p>
          <p class="empty__hint">
            Die Antwort nennt ihre Belege als Nummern wie [1]. Ein Klick darauf öffnet den passenden
            Textauszug.
          </p>
          <p
            v-if="status !== null && status !== 'offline' && status.chunks_im_index === 0"
            class="empty__hint"
          >
            Der Index ist noch leer: Dokumente nach <code>backend/docs/</code> legen und
            <code>uv run python ingest.py</code> ausführen.
          </p>
        </div>
        <ChatMessage
          v-for="message in messages"
          :key="message.id"
          :message="message"
          @retry="(question) => onRetry(message.id, question)"
        />
      </div>
    </main>

    <footer class="footer">
      <div class="footer__inner">
        <ChatInput :disabled="isLoading" @submit="onSubmit" />
      </div>
    </footer>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.header {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.25rem 1rem;
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
}

.header__title {
  margin: 0;
  font-size: 1.15rem;
}

.header__status {
  margin: 0;
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.header__status--offline {
  color: var(--color-error-text);
}

.header__recheck {
  margin-left: 0.4rem;
  padding: 0;
  border: none;
  background: none;
  color: var(--color-accent);
  font: inherit;
  text-decoration: underline;
  cursor: pointer;
}

.history {
  flex: 1;
  overflow-y: auto;
}

.history__inner,
.footer__inner {
  max-width: 50rem;
  margin: 0 auto;
  padding: 1rem;
}

.history__inner {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.empty {
  margin: 3rem auto 0;
  max-width: 32rem;
  text-align: center;
  color: var(--color-text-muted);
}

.empty__title {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  color: var(--color-text);
}

.empty__hint {
  margin: 0 0 0.5rem;
  font-size: 0.9rem;
}

.empty code {
  font-family: var(--font-mono);
  font-size: 0.85em;
}

.footer {
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
}
</style>
