<script setup lang="ts">
import { nextTick, ref } from 'vue'

import type { Source } from '@/types/api'

const props = defineProps<{ sources: Source[] }>()

const openStates = ref<boolean[]>(props.sources.map(() => false))
const highlighted = ref<number | null>(null)
const itemEls: (HTMLElement | null)[] = []
let highlightTimer: ReturnType<typeof setTimeout> | undefined

function onToggle(index: number, event: Event) {
  openStates.value[index] = (event.target as HTMLDetailsElement).open
}

function formatLabel(source: Source): string {
  return source.page ? `${source.source}, S. ${source.page}` : source.source
}

// Springt zur Quelle mit Belegnummer n (1-basiert), klappt sie auf und hebt sie kurz hervor
async function reveal(n: number) {
  const index = n - 1
  const el = itemEls[index]
  if (!el) return

  openStates.value[index] = true
  await nextTick()

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  el.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'nearest' })
  el.querySelector('summary')?.focus({ preventScroll: true })

  highlighted.value = index
  clearTimeout(highlightTimer)
  highlightTimer = setTimeout(() => (highlighted.value = null), 1600)
}

defineExpose({ reveal })
</script>

<template>
  <section class="sources" aria-label="Quellen">
    <h3 class="sources__title">Quellen</h3>
    <ol class="sources__list">
      <li v-for="(source, index) in sources" :key="index">
        <details
          :ref="(el) => (itemEls[index] = el as HTMLElement | null)"
          class="source"
          :class="{ 'source--highlight': highlighted === index }"
          :open="openStates[index]"
          @toggle="onToggle(index, $event)"
        >
          <summary class="source__summary">
            <span class="source__number">[{{ index + 1 }}]</span>
            <span class="source__label">{{ formatLabel(source) }}</span>
            <span class="source__distance" title="Kosinus-Distanz: kleiner ist ähnlicher">
              Distanz {{ source.distance.toFixed(3) }}
            </span>
          </summary>
          <blockquote class="source__text">{{ source.text }}</blockquote>
        </details>
      </li>
    </ol>
  </section>
</template>

<style scoped>
.sources {
  margin-top: 0.9rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.sources__title {
  margin: 0 0 0.4rem;
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.sources__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.source {
  border: 1px solid var(--color-border);
  border-radius: calc(var(--radius) - 4px);
  background: var(--color-surface-muted);
  scroll-margin: 1rem;
  transition: background-color 0.4s ease, border-color 0.4s ease;
}

.source--highlight {
  background: var(--color-highlight);
  border-color: var(--color-accent);
}

.source__summary {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.25rem 0.6rem;
  padding: 0.4rem 0.65rem;
  cursor: pointer;
  font-size: 0.9rem;
}

.source__summary:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
  border-radius: calc(var(--radius) - 4px);
}

.source__number {
  font-weight: 600;
  color: var(--color-accent);
}

.source__label {
  flex: 1 1 auto;
  min-width: 0;
  overflow-wrap: anywhere;
}

.source__distance {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.source__text {
  margin: 0;
  padding: 0.6rem 0.8rem 0.75rem;
  border-top: 1px solid var(--color-border);
  font-size: 0.875rem;
  white-space: pre-wrap;
  color: var(--color-text-muted);
}

@media (prefers-reduced-motion: reduce) {
  .source {
    transition: none;
  }
}
</style>
