<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h3>✏️ Редактировать члена семьи</h3>

      <label>ФИО</label>
      <input v-model="fullName" placeholder="Иванов Иван Иванович" type="text" />

      <label>Родство</label>
      <select v-model="kinship">
        <option disabled value="">— выберите —</option>
        <option v-for="k in kinshipTypes" :key="k" :value="k">{{ k }}</option>
      </select>

      <p v-if="error" class="error">{{ error }}</p>

      <div class="modal-actions">
        <button @click="submit" :disabled="!valid">Сохранить</button>
        <button @click="$emit('close')">Отмена</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '../api'

const props = defineProps({ member: Object })
const emit = defineEmits(['close', 'updated'])

const kinshipTypes = ['мать', 'отец', 'сын', 'дочь', 'бабушка', 'дедушка']
const fullName = ref(props.member.full_name)
const kinship = ref(props.member.kinship_type)
const error = ref('')

const valid = computed(() => fullName.value.trim() && kinship.value)

const submit = async () => {
  try {
    await api.put(`/members/${props.member.id}`, {
      full_name: fullName.value.trim(),
      kinship_type: kinship.value
    })
    emit('updated')
    emit('close')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка обновления'
  }
}
</script>

<style scoped>
/* стили уже есть в App.vue, можно не дублировать */
</style>