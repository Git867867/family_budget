<template>
  <div class="history-view">
    <h2 class="page-title">История</h2>

    <!-- Вкладки -->
    <div class="tabs">
      <button
        :class="{ active: activeTab === 'audit' }"
        @click="activeTab = 'audit'"
      >
        Журнал действий
      </button>
      <button
        :class="{ active: activeTab === 'balance' }"
        @click="activeTab = 'balance'"
      >
        Динамика баланса
      </button>
    </div>

    <!-- Журнал аудита -->
    <div v-if="activeTab === 'audit'">
      <div class="filters">
        <label>С:</label>
        <input type="date" v-model="auditStartDate" />
        <label>По:</label>
        <input type="date" v-model="auditEndDate" />
        <label>Действие:</label>
        <select v-model="auditAction">
          <option value="">Все</option>
          <option v-for="a in auditActions" :key="a" :value="a">{{ a }}</option>
        </select>
        <button class="primary" @click="fetchAudit">Показать</button>
      </div>

      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Дата/время</th>
              <th>Пользователь</th>
              <th>Действие</th>
              <th>ID сущности</th>
              <th>Детали</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in auditLogs" :key="log.id">
              <td>{{ formatDateTime(log.created_at) }}</td>
              <td>{{ getUserName(log) }}</td>
              <td>{{ log.action }}</td>
              <td>{{ log.entity_id || '—' }}</td>
              <td>{{ log.details || '—' }}</td>
            </tr>
            <tr v-if="auditLogs.length === 0">
              <td colspan="5" class="text-center">Нет записей</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Динамика баланса -->
    <div v-if="activeTab === 'balance'">
      <div class="filters">
        <label>С:</label>
        <input type="date" v-model="balanceStartDate" />
        <label>По:</label>
        <input type="date" v-model="balanceEndDate" />
        <button class="primary" @click="fetchBalanceHistory">Показать</button>
      </div>

      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Дата/время</th>
              <th>Тип операции</th>
              <th v-if="role === 'admin'">ID операции</th>
              <th class="text-right">Сумма изменения</th>
              <th class="text-right">Баланс до</th>
              <th class="text-right">Баланс после</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in balanceHistory" :key="idx">
              <td>{{ formatDateTime(item.changed_at) }}</td>
              <td>{{ item.operation_type }}</td>
              <td v-if="role === 'admin'">{{ item.operation_id || '—' }}</td>
              <td class="text-right font-mono">{{ formatAmount(item.change_amount) }}</td>
              <td class="text-right font-mono">{{ formatAmount(item.balance_before) }}</td>
              <td class="text-right font-mono">{{ formatAmount(item.balance_after) }}</td>
            </tr>
            <tr v-if="balanceHistory.length === 0">
              <td :colspan="role === 'admin' ? 6 : 5" class="text-center">Нет данных</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const role = localStorage.getItem('role') || 'guest'

const activeTab = ref('audit')

// Фильтры аудита
const auditStartDate = ref('')
const auditEndDate = ref('')
const auditAction = ref('')
const auditLogs = ref([])
const auditActions = ref([])

// Фильтры баланса
const balanceStartDate = ref('')
const balanceEndDate = ref('')
const balanceHistory = ref([])

const formatDateTime = (iso) => {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleString('ru-RU')
}

const formatAmount = (val) => {
  if (val === undefined || val === null) return '—'
  return new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(val)
}

const getUserName = (log) => {
  if (log.user_role === 'admin') return 'Администратор'
  if (log.user_role === 'guest') return 'Гость'
  return `ID:${log.user_id}`
}

const fetchAudit = async () => {
  const params = {}
  if (auditStartDate.value) params.start_date = auditStartDate.value
  if (auditEndDate.value) params.end_date = auditEndDate.value
  if (auditAction.value) params.action = auditAction.value
  try {
    const res = await api.get('/audit', { params })
    auditLogs.value = res.data
    // собрать уникальные действия для фильтра
    if (auditActions.value.length === 0 && res.data.length) {
      const actions = new Set()
      res.data.forEach(log => actions.add(log.action))
      auditActions.value = Array.from(actions).sort()
    }
  } catch (e) {
    console.error(e)
    auditLogs.value = []
  }
}

const fetchBalanceHistory = async () => {
  const params = {}
  if (balanceStartDate.value) params.start_date = balanceStartDate.value
  if (balanceEndDate.value) params.end_date = balanceEndDate.value
  try {
    const res = await api.get('/balance/history', { params })
    balanceHistory.value = res.data
  } catch (e) {
    console.error(e)
    balanceHistory.value = []
  }
}

onMounted(() => {
  if (role !== 'guest') {
    fetchAudit()
    fetchBalanceHistory()
  }
})
</script>

<style scoped>
.history-view {
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
.tabs {
  display: flex;
  gap: 12px;
  border-bottom: 1px solid #E2E8F0;
  padding-bottom: 8px;
}
.tabs button {
  background: none;
  border: none;
  padding: 8px 16px;
  font-size: 15px;
  font-weight: 500;
  color: #64748B;
  cursor: pointer;
  border-radius: 8px;
}
.tabs button.active {
  color: #3B82F6;
  background: #EFF6FF;
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
}
.filters label {
  font-size: 13px;
  font-weight: 500;
  color: #475569;
}
.filters input, .filters select {
  padding: 8px 12px;
  border: 1px solid #CBD5E1;
  border-radius: 8px;
  font-size: 14px;
}
.text-right {
  text-align: right;
}
.font-mono {
  font-variant-numeric: tabular-nums;
}
.text-center {
  text-align: center;
}
</style>