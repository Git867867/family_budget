<template>
  <div>
    <div class="filters">
      <label>С:</label>
      <input
        ref="startDateInput"
        type="date"
        v-model="startDate"
        @click="openStartDatePicker"
      />
      <label>По:</label>
      <input
        ref="endDateInput"
        type="date"
        v-model="endDate"
        @click="openEndDatePicker"
      />
      <button class="primary" @click="fetchData">Показать</button>
    </div>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Тип дохода</th>
            <th>Член семьи</th>
            <th class="text-right">Сумма</th>
            <th>Дата</th>
            <th v-if="role !== 'guest'" class="text-center">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in incomes" :key="item.id">
            <td>{{ item.income_type }}</td>
            <td>{{ item.full_name }} ({{ item.kinship_type }})</td>
            <td class="text-right font-mono">{{ formatAmount(item.amount) }}</td>
            <td>{{ formatDate(item.date) }}</td>
            <td v-if="role !== 'guest'" class="text-center actions-cell">
              <button class="icon-btn" @click="$emit('edit', item)" title="Редактировать">✎</button>
              <button class="icon-btn danger" @click="deleteItem(item.id)" title="Удалить">✕</button>
            </td>
          </tr>
          <tr v-if="incomes.length" class="total">
            <td colspan="2">Итого</td>
            <td class="text-right font-mono">{{ formatAmount(total) }}</td>
            <td></td>
            <td v-if="role !== 'guest'"></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const props = defineProps({
  role: { type: String, default: 'guest' }
})
const emit = defineEmits(['edit', 'updated'])

const startDate = ref('')
const endDate = ref('')
const incomes = ref([])
const total = ref(0)

const startDateInput = ref(null)
const endDateInput = ref(null)

const openStartDatePicker = () => {
  if (startDateInput.value && startDateInput.value.showPicker) startDateInput.value.showPicker()
}
const openEndDatePicker = () => {
  if (endDateInput.value && endDateInput.value.showPicker) endDateInput.value.showPicker()
}

const fetchData = async () => {
  const params = {}
  if (startDate.value) params.start_date = startDate.value
  if (endDate.value) params.end_date = endDate.value
  try {
    const res = await api.get('/incomes', { params })
    incomes.value = res.data
    total.value = res.data.reduce((sum, item) => sum + Number(item.amount), 0)
  } catch (e) {
    incomes.value = []
    total.value = 0
  }
}

const deleteItem = async (id) => {
  if (confirm('Удалить доход?')) {
    await api.delete(`/income/${id}`)
    emit('updated')
  }
}

const formatAmount = (val) => {
  if (val === undefined || val === null) return '—'
  return new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(val)
}

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('ru-RU')
}

onMounted(fetchData)
defineExpose({ fetchData })
</script>

<style scoped>
.filters {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.filters label {
  font-size: 13px;
  font-weight: 500;
  color: #475569;
}
.filters input {
  padding: 6px 10px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
}
.filters button {
  margin-left: 4px;
}
.actions-cell {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}
</style>