<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h3>Добавить члена семьи</h3>

      <label>ФИО</label>
      <input v-model="fullName" placeholder="Иванов Иван Иванович" type="text" />

      <label>Родство</label>
      <select v-model="kinship">
        <option disabled value="">— выберите —</option>
        <option v-for="k in kinshipTypes" :key="k" :value="k">{{ k }}</option>
      </select>

      <p v-if="error" class="error">{{ error }}</p>

      <div class="modal-actions">
        <button @click="submit" :disabled="!valid">Добавить</button>
        <button @click="$emit('close')">Отмена</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '../api'

const emit = defineEmits(['close', 'added'])

const kinshipTypes = ['мать', 'отец', 'сын', 'дочь', 'бабушка', 'дедушка']
const fullName = ref('')
const kinship = ref('')
const error = ref('')

const valid = computed(() => fullName.value.trim() && kinship.value)

const submit = async () => {
  try {
    await api.post('/members', {
      full_name: fullName.value.trim(),
      kinship_type: kinship.value
    })
    emit('added')
    emit('close')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка'
  }
}
</script>