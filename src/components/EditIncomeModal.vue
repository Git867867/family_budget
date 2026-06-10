<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h3>Редактировать доход</h3>

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

const incomeTypes = ['зарплата', 'стипендия', 'пенсия', 'дополнительный заработок']
const accounts = ['основной счет', 'накопления', 'заначка']

const form = reactive({
  income_type: '',
  account: '',
  amount: 0,
  date: ''
})
const amountRaw = ref('')
const dateInput = ref(null)
const error = ref('')

onMounted(() => {
  if (props.item) {
    form.income_type = props.item.income_type
    form.account = props.item.account
    form.amount = props.item.amount
    form.date = props.item.date
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
    await api.put(`/income/${props.item.id}`, {
      income_type: form.income_type,
      account: form.account,
      amount: form.amount,
      date: form.date
    })
    emit('updated')
    emit('close')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка'
  }
}
</script>