<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h3>Добавить доход</h3>

      <label>Тип дохода</label>
      <select v-model="form.income_type">
        <option disabled value="">— выберите —</option>
        <option v-for="t in incomeTypes" :key="t" :value="t">{{ t }}</option>
      </select>

      <label>Счёт</label>
      <select v-model="form.account">
        <option disabled value="">— выберите —</option>
        <option v-for="a in accounts" :key="a" :value="a">{{ a }}</option>
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

const incomeTypes = ['зарплата', 'стипендия', 'пенсия', 'дополнительный заработок']
const accounts = ['основной счет', 'накопления', 'заначка']

const form = reactive({
  income_type: '',
  account: '',
  amount: 0,
  date: new Date().toISOString().slice(0, 10),
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
  const base = form.income_type && form.account && form.amount > 0 && form.date
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
      income_type: form.income_type,
      account: form.account,
      amount: form.amount,
      date: form.date
    }
    if (props.role === 'admin') payload.member_id = form.member_id
    await api.post('/income', payload)
    emit('added')
    emit('close')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка'
  }
}
</script>