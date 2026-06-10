<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h3>Редактировать расход</h3>

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

      <p v-if="error" class="error">{{ error }}</p>

      <div class="modal-actions">
        <button @click="submit">Сохранить</button>
        <button @click="$emit('close')">Отмена</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import api from '../api'

const props = defineProps({
  item: Object
})
const emit = defineEmits(['close', 'updated'])

const categories = [
  'продукты', 'одежда', 'коммунальные услуги', 'мобильная связь',
  'отдых', 'обучение', 'развлечения', 'лекарства', 'транспорт', 'другое'
]

const form = reactive({
  category: '',
  amount: 0,
  date: '',
  is_planned: false
})
const amountRaw = ref('')
const dateInput = ref(null)
const error = ref('')

onMounted(() => {
  if (props.item) {
    form.category = props.item.category
    form.amount = props.item.amount
    form.date = props.item.date
    form.is_planned = props.item.is_planned
    amountRaw.value = form.amount.toFixed(2).replace('.', ',')
  }
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
    await api.put(`/expense/${props.item.id}`, {
      category: form.category,
      amount: form.amount,
      date: form.date,
      is_planned: form.is_planned
    })
    emit('updated')
    emit('close')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка'
  }
}
</script>