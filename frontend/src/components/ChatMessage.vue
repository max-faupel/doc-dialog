<script setup lang="ts">
import { computed, ref } from 'vue'

import SourceList from '@/components/SourceList.vue'
import type { ChatMessage } from '@/types/chat'
import { parseCitations } from '@/utils/citations'

const props = defineProps<{ message: ChatMessage }>()
const emit = defineEmits<{ retry: [question: string] }>()

const sourceList = ref<InstanceType<typeof SourceList> | null>(null)

const segments = computed(() =>
  props.message.role === 'assistant' && props.message.status === 'done'
    ? parseCitations(props.message.text, props.message.sources.length)
    : [],
)
</script>

<template>
  <article v-if="message.role === 'user'" class="message message--user">
    <p class="message__text">{{ message.text }}</p>
  </article>

  <article
    v-else-if="message.status === 'loading'"
    class="message message--assistant"
    aria-busy="true"
  >
    <p class="message__loading">
      <span class="dots" aria-hidden="true"><span></span><span></span><span></span></span>
      Durchsuche Dokumente und formuliere Antwort …
    </p>
  </article>

  <article v-else-if="message.status === 'error'" class="message message--error" role="alert">
    <p class="message__error-title">
      {{ message.errorKind === 'network' ? 'Backend nicht erreichbar' : 'Anfrage fehlgeschlagen' }}
    </p>
    <p class="message__text">{{ message.text }}</p>
    <button type="button" class="retry" @click="emit('retry', message.question)">
      Erneut versuchen
    </button>
  </article>

  <article v-else class="message message--assistant">
    <p class="message__text">
      <template v-for="(segment, i) in segments" :key="i">
        <template v-if="segment.type === 'text'">{{ segment.value }}</template>
        <span v-else class="cite"
          >[<template v-for="(ref_, j) in segment.refs" :key="j"
            ><template v-if="j > 0">, </template
            ><button
              v-if="ref_.valid"
              type="button"
              class="cite__link"
              :aria-label="`Zur Quelle ${ref_.n} springen`"
              @click="sourceList?.reveal(ref_.n)"
            >
              {{ ref_.n }}</button
            ><template v-else>{{ ref_.n }}</template></template
          >]</span
        >
      </template>
    </p>
    <SourceList v-if="message.sources.length" ref="sourceList" :sources="message.sources" />
  </article>
</template>

<style scoped>
.message {
  max-width: 100%;
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
}

.message--user {
  align-self: flex-end;
  max-width: 85%;
  background: var(--color-user-bubble);
  color: var(--color-user-text);
}

.message--assistant {
  align-self: stretch;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
}

.message--error {
  align-self: stretch;
  background: var(--color-error-bg);
  border: 1px solid var(--color-error-border);
  color: var(--color-error-text);
}

.message__text {
  margin: 0;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.message__error-title {
  margin: 0 0 0.25rem;
  font-weight: 600;
}

.message__loading {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  color: var(--color-text-muted);
}

.cite {
  white-space: nowrap;
  color: var(--color-text-muted);
}

.cite__link {
  padding: 0 0.1rem;
  border: none;
  background: none;
  font: inherit;
  font-weight: 600;
  color: var(--color-accent);
  text-decoration: underline;
  text-underline-offset: 2px;
  cursor: pointer;
}

.cite__link:hover {
  text-decoration-thickness: 2px;
}

.cite__link:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 1px;
  border-radius: 3px;
}

.retry {
  margin-top: 0.6rem;
  padding: 0.35rem 0.8rem;
  border: 1px solid currentColor;
  border-radius: 6px;
  background: transparent;
  color: inherit;
  font: inherit;
  font-size: 0.9rem;
  cursor: pointer;
}

.dots {
  display: inline-flex;
  gap: 4px;
}

.dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-accent);
  animation: pulse 1.2s infinite ease-in-out;
}

.dots span:nth-child(2) {
  animation-delay: 0.15s;
}

.dots span:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes pulse {
  0%,
  80%,
  100% {
    opacity: 0.25;
    transform: scale(0.8);
  }
  40% {
    opacity: 1;
    transform: scale(1);
  }
}

@media (prefers-reduced-motion: reduce) {
  .dots span {
    animation: none;
    opacity: 0.6;
  }
}
</style>
