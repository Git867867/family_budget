<template>
  <div class="report-view">
    <h2 class="page-title">Отчёт за период</h2>
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
      <button class="primary" @click="fetchReport">Показать</button>
      <button class="success" @click="exportExcel">Экспорт в Excel</button>
    </div>

    <div v-if="reportData" class="table-container">
      <table>
        <thead>
          <tr>
            <th>Статья</th>
            <th>Кто</th>
            <th class="text-right">Сумма</th>
            <th>Дата</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="reportData.incomes?.length">
            <tr class="section-header"><td colspan="4">Доход</td></tr>
            <tr v-for="(inc, idx) in reportData.incomes" :key="'inc-'+idx">
              <td>{{ inc.income_type }}</td>
              <td>{{ inc.full_name }} ({{ inc.kinship_type }})</td>
              <td class="text-right font-mono">{{ formatAmount(inc.amount) }}</td>
              <td>{{ formatDate(inc.date) }}</td>
            </tr>
          </template>
          <template v-if="reportData.expenses?.length">
            <tr class="section-header"><td colspan="4">Расход</td></tr>
            <tr v-for="(exp, idx) in reportData.expenses" :key="'exp-'+idx">
              <td>{{ exp.category }}</td>
              <td></td>
              <td class="text-right font-mono">{{ formatAmount(exp.amount) }}</td>
              <td>{{ formatDate(exp.date) }}</td>
            </tr>
          </template>
          <tr class="total"><td colspan="2">Итого</td><td colspan="2"></td></tr>
          <tr><td>Доход</td><td></td><td class="text-right font-mono">{{ formatAmount(reportData.total_income) }}</td><td></td></tr>
          <tr><td>Расход</td><td></td><td class="text-right font-mono">{{ formatAmount(reportData.total_expense) }}</td><td></td></tr>
          <tr class="total"><td>Баланс</td><td></td><td class="text-right font-mono font-bold">{{ formatAmount(reportData.balance) }}</td><td></td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const startDate = ref(new Date().toISOString().slice(0, 7) + '-01')
const endDate = ref(new Date().toISOString().slice(0, 10))
const reportData = ref(null)

const startDateInput = ref(null)
const endDateInput = ref(null)

const openStartDatePicker = () => {
  if (startDateInput.value && startDateInput.value.showPicker) startDateInput.value.showPicker()
}
const openEndDatePicker = () => {
  if (endDateInput.value && endDateInput.value.showPicker) endDateInput.value.showPicker()
}

const fetchReport = async () => {
  if (!startDate.value || !endDate.value) return
  try {
    const res = await api.get('/report', {
      params: { start_date: startDate.value, end_date: endDate.value }
    })
    reportData.value = res.data
  } catch (e) {
    alert('Ошибка получения отчёта')
  }
}

const exportExcel = async () => {
  if (!startDate.value || !endDate.value) return
  try {
    const response = await api.get('/export/excel', {
      params: { start_date: startDate.value, end_date: endDate.value },
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `Семейный_бюджет_${startDate.value}_${endDate.value}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (e) {
    alert('Ошибка экспорта')
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

onMounted(fetchReport)
</script>

<style scoped>
.report-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #1E293B;
  margin: 0;
}
.filters {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  flex-wrap: wrap;
  padding: 16px 20px;
  background: #FFFFFF;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
}
.filters label {
  font-size: 13px;
  font-weight: 500;
  color: #475569;
}
.filters input {
  padding: 8px 12px;
  border: 1px solid #CBD5E1;
  border-radius: 8px;
}
.filters button {
  margin-left: 4px;
}
.section-header {
  background-color: #F8FAFC;
  font-weight: 600;
  color: #475569;
}
.section-header td {
  padding: 8px 20px;
}
.text-right { text-align: right; }
.font-mono { font-variant-numeric: tabular-nums; }
.font-bold { font-weight: 600; }
</style>