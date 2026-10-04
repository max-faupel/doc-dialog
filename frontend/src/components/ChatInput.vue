<script setup lang="ts">
import { computed, ref } from 'vue'

const MIN_LENGTH = 3

const props = defineProps<{ disabled: boolean }>()
const emit = defineEmits<{ submit: [question: string] }>()

const text = ref('')
const canSubmit = computed(() => !props.disabled && text.value.trim().length >= MIN_LENGTH)

function submit() {
  if (!canSubmit.value) return
  emit('submit', text.value.trim())
  text.value = ''
}

// Enter sendet, Shift+Enter fügt eine neue Zeile ein (nicht während IME-Eingabe)
function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault()
    submit()
  }
}
</script>

<template>
  <form class="input" @submit.prevent="submit">
    <label for="question" class="visually-hidden">Frage an die Dokumente</label>
    <textarea
      id="question"
      v-model="text"
      class="input__field"
      rows="2"
      placeholder="Frage an deine Dokumente stellen … (Enter sendet, Shift+Enter für neue Zeile)"
      @keydown="onKeydown"
    ></textarea>
    <button type="submit" class="input__button" :disabled="!canSubmit">
      {{ disabled ? 'Warte …' : 'Fragen' }}
    </button>
  </form>
</template>

<style scoped>
.input {
  display: flex;
  gap: 0.6rem;
  align-items: flex-end;
}

.input__field {
  flex: 1;
  min-height: 3rem;
  max-height: 12rem;
  padding: 0.65rem 0.8rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
  color: var(--color-text);
  font: inherit;
  resize: vertical;
}

.input__field:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 1px;
}

.input__button {
  padding: 0.7rem 1.2rem;
  border: none;
  border-radius: var(--radius);
  background: var(--color-accent);
  color: var(--color-accent-contrast);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

.input__button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input__button:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}
</style>
