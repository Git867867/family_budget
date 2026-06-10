<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h3>Добавить расход</h3>

      <label>Категория</label>
      <select v-model="form.category">
        <option disabled value="">— выберите —</option>
        <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
      </select>

      <label>Сумма</label>
      <input
        v-model="amountRaw"
        type="text"
        inputmode="decimal"
        placeholder="0.00"
        @input="validateAmount"
        @blur="formatAmount"
      />

      <label>Дата</label>
      <input ref="dateInput" type="date" v-model="form.date" @click="openDatePicker" />

      <label class="checkbox-label">
        <input type="checkbox" v-model="form.is_planned" />
        Плановый расход
      </label>

      <div v-if="role === 'admin'">
        <label>Член семьи (для кого)</label>
        <select v-model="form.member_id">
          <option disabled value="">— выберите —</option>
          <option v-for="m in members" :key="m.id" :value="m.id">
            {{ m.full_name }} ({{ m.kinship_type }})
          </option>
        </select>
      </div>

      <p v-if="error" class="error">{{ error }}</p>

      <div class="modal-actions">
        <button @click="submit" :disabled="!valid">Добавить</button>
        <button @click="$emit('close')">Отмена</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed, ref, watch } from 'vue'
import api from '../api'

const props = defineProps({
  role: { type: String, default: '' },
  members: { type: Array, default: () => [] }
})

const emit = defineEmits(['close', 'added'])

const categories = [
  'продукты', 'одежда', 'коммунальные услуги', 'мобильная связь',
  'отдых', 'обучение', 'развлечения', 'лекарства', 'транспорт', 'другое'
]

const form = reactive({
  category: '',
  amount: 0,
  date: new Date().toISOString().slice(0, 10),
  is_planned: false,
  member_id: null
})

const amountRaw = ref('')
const dateInput = ref(null)
const error = ref('')

watch(() => props.members, (newMembers) => {
  if (props.role === 'admin' && newMembers.length > 0 && !form.member_id) {
    form.member_id = newMembers[0].id
  }
}, { immediate: true })

const valid = computed(() => {
  const base = form.category && form.amount > 0 && form.date
  if (props.role === 'admin') return base && form.member_id !== null
  return base
})

const validateAmount = () => {
  let value = amountRaw.value.replace(',', '.')
  value = value.replace(/[^0-9.]/g, '')
  const parts = value.split('.')
  if (parts.length > 2) value = parts[0] + '.' + parts.slice(1).join('')
  if (parts[1] && parts[1].length > 2) value = parts[0] + '.' + parts[1].slice(0, 2)
  amountRaw.value = value
  const num = parseFloat(value)
  form.amount = isNaN(num) ? 0 : num
}

const formatAmount = () => {
  if (form.amount === 0 || isNaN(form.amount)) {
    amountRaw.value = ''
  } else {
    amountRaw.value = form.amount.toFixed(2).replace('.', ',')
  }
}

const openDatePicker = () => {
  if (dateInput.value && dateInput.value.showPicker) {
    dateInput.value.showPicker()
  }
}

const submit = async () => {
  try {
    const payload = {
      category: form.category,
      amount: form.amount,
      date: form.date,
      is_planned: form.is_planned
    }
    if (props.role === 'admin') payload.member_id = form.member_id
    await api.post('/expense', payload)
    emit('added')
    emit('close')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка'
  }
}
</script>