<template>
  <div class="dashboard">
    <!-- Панель действий — скрыта для гостя -->
    <div class="action-bar" v-if="canModifyFinances">
      <button class="success" @click="showAddIncome = true" v-if="canModifyFinances">
        <span>+</span> Доход
      </button>
      <button class="primary" @click="showAddExpense = true" v-if="canModifyFinances">
        <span>−</span> Расход
      </button>
      <div class="spacer"></div>
      <button class="outline" @click="uploadMembers" v-if="isAdminOrClient">
        Загрузить (JSON)
      </button>
      <button class="outline" @click="exportMembers" v-if="isAdminOrClient">
        Экспорт (JSON)
      </button>
    </div>

    <!-- Сетка таблиц -->
    <div class="tables-grid">
      <div class="table-wrapper">
        <div class="table-header">
          <h3>Доходы</h3>
        </div>
        <IncomeTable ref="incomeTable" @edit="openEditIncome" @updated="refreshAll" :role="role" />
      </div>
      <div class="table-wrapper">
        <div class="table-header">
          <h3>Расходы</h3>
        </div>
        <ExpenseTable ref="expenseTable" @edit="openEditExpense" @updated="refreshAll" :role="role" />
      </div>
    </div>

    <!-- Таблица членов семьи (только для admin) -->
    <MembersTable
      v-if="isAdmin"
      :members="members"
      @add="showAddMember = true"
      @edit="openEditMember"
      @delete="deleteMember"
    />

    <!-- Модальные окна -->
    <AddIncomeModal
      v-if="showAddIncome"
      @close="showAddIncome = false"
      @added="refreshAll"
      :role="role"
      :members="members"
    />
    <AddExpenseModal
      v-if="showAddExpense"
      @close="showAddExpense = false"
      @added="refreshAll"
      :role="role"
      :members="members"
    />
    <AddMemberModal v-if="showAddMember" @close="showAddMember = false" @added="refreshMembers" />
    <EditMemberModal v-if="editingMember" :member="editingMember" @close="editingMember = null" @updated="refreshMembers" />
    <EditIncomeModal v-if="editingIncome" :item="editingIncome" @close="editingIncome = null" @updated="refreshAll" />
    <EditExpenseModal v-if="editingExpense" :item="editingExpense" @close="editingExpense = null" @updated="refreshAll" />
  </div>
</template>

<script setup>
import { ref, computed, inject, onMounted } from 'vue'
import IncomeTable from '../components/IncomeTable.vue'
import ExpenseTable from '../components/ExpenseTable.vue'
import AddIncomeModal from '../components/AddIncomeModal.vue'
import AddExpenseModal from '../components/AddExpenseModal.vue'
import AddMemberModal from '../components/AddMemberModal.vue'
import EditMemberModal from '../components/EditMemberModal.vue'
import MembersTable from '../components/MembersTable.vue'
import EditIncomeModal from '../components/EditIncomeModal.vue'
import EditExpenseModal from '../components/EditExpenseModal.vue'
import api from '../api'

const showAddIncome = ref(false)
const showAddExpense = ref(false)
const showAddMember = ref(false)
const editingIncome = ref(null)
const editingExpense = ref(null)
const editingMember = ref(null)
const members = ref([])

const role = localStorage.getItem('role') || ''
const isAdmin = computed(() => role === 'admin')
const isAdminOrClient = computed(() => role === 'admin' || role === 'client')
const canModifyFinances = computed(() => role === 'client' || role === 'admin')

const fetchBalance = inject('fetchBalance')
const incomeTable = ref(null)
const expenseTable = ref(null)

function refreshAll() {
  fetchBalance()
  if (incomeTable.value) incomeTable.value.fetchData()
  if (expenseTable.value) expenseTable.value.fetchData()
}

function refreshMembers() {
  loadMembers()
}

function openEditIncome(item) {
  editingIncome.value = item
}
function openEditExpense(item) {
  editingExpense.value = item
}
function openEditMember(member) {
  editingMember.value = member
}

async function deleteMember(member) {
  if (!confirm(`Удалить члена семьи "${member.full_name}"? Все связанные доходы и расходы также будут удалены.`)) return
  try {
    await api.delete(`/members/${member.id}`)
    refreshMembers()
    refreshAll() // обновить таблицы на случай, если у удалённого были операции
  } catch (e) {
    alert(e.response?.data?.detail || 'Ошибка удаления')
  }
}

async function loadMembers() {
  try {
    const res = await api.get('/members')
    members.value = res.data
  } catch (err) {
    console.error('Ошибка загрузки членов семьи:', err)
    members.value = []
  }
}

function uploadMembers() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    try {
      await api.post('/members/upload', formData)
      alert('Члены семьи успешно загружены')
      loadMembers()
    } catch (err) {
      alert('Ошибка загрузки: ' + (err.response?.data?.detail || err.message))
    }
  }
  input.click()
}

async function exportMembers() {
  try {
    const response = await api.get('/members')
    const json = JSON.stringify(response.data, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'family_members.json')
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    alert('Ошибка экспорта: ' + (err.response?.data?.detail || err.message))
  }
}

onMounted(() => {
  if (isAdminOrClient.value) {
    loadMembers()
  }
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.action-bar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
  background: #FFFFFF;
  padding: 16px 20px;
  border-radius: 16px;
  border: 1px solid #E2E8F0;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.03);
}

.action-bar button {
  padding: 8px 16px;
}

.action-bar .spacer {
  flex: 1;
}

.tables-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.table-wrapper {
  background: #FFFFFF;
  border-radius: 16px;
  border: 1px solid #E2E8F0;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.03);
  padding: 20px;
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
  margin: 0;
}

@media (max-width: 1024px) {
  .tables-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .action-bar {
    flex-direction: column;
    align-items: stretch;
  }
  .action-bar .spacer {
    display: none;
  }
}
</style>