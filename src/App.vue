<template>
  <div id="app">
    <header v-if="currentUser">
      <nav>
        <router-link to="/dashboard">Главная</router-link>
        <router-link to="/report">Отчёт</router-link>
        <router-link v-if="currentUser && (currentUser.role === 'admin' || currentUser.role === 'client')" to="/history">История</router-link>
        <a href="#" @click.prevent="logout">Выход</a>
      </nav>
      <StatusBar :balance="balance" :user="currentUser" />
    </header>
    <main>
      <router-view @login="onLogin" />
    </main>
  </div>
</template>

<script setup>
import { ref, provide, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from './api'
import StatusBar from './components/StatusBar.vue'

const router = useRouter()
const currentUser = ref(null)
const balance = ref({})

onMounted(async () => {
  const token = localStorage.getItem('token')
  if (token) {
    try {
      const res = await api.get('/balance')
      balance.value = res.data
      const userName = localStorage.getItem('userName') || 'Пользователь'
      currentUser.value = { full_name: userName, role: localStorage.getItem('role') || 'guest' }
      router.push('/dashboard')
    } catch (e) {
      localStorage.clear()
      router.push('/')
    }
  }
})

const onLogin = (userData) => {
  currentUser.value = userData
  localStorage.setItem('userName', userData.full_name)
  localStorage.setItem('role', userData.role)
  fetchBalance()
}

const fetchBalance = async () => {
  try {
    const res = await api.get('/balance')
    balance.value = res.data
  } catch (e) {
    balance.value = {}
  }
}

const logout = async () => {
  try {
    await api.post('/session/end')
  } finally {
    localStorage.clear()
    currentUser.value = null
    balance.value = {}
    router.push('/')
  }
}

provide('fetchBalance', fetchBalance)
</script>

<style>
/* все стили остаются без изменений */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background-color: #f8fafc;
  color: #1e293b;
  -webkit-font-smoothing: antialiased;
  line-height: 1.5;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
  padding: 24px 32px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

/* ---------- Header ---------- */
header {
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  padding: 12px 32px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
}

header nav {
  display: flex;
  gap: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

header nav a {
  color: #64748b;
  text-decoration: none;
  font-weight: 500;
  font-size: 15px;
  transition: color 0.2s;
  padding: 4px 0;
  position: relative;
  white-space: nowrap;
}

header nav a::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #3b82f6;
  transform: scaleX(0);
  transition: transform 0.2s;
}

header nav a.router-link-active::after {
  transform: scaleX(1);
}

header nav a:hover,
header nav a.router-link-active {
  color: #1e293b;
}

header nav a:last-child {
  color: #ef4444;
  margin-left: auto;
}

header nav a:last-child:hover {
  color: #dc2626;
}

/* ---------- Status Bar ---------- */
.status-bar {
  display: flex;
  gap: 32px;
  flex-wrap: wrap;
  color: #64748b;
  font-size: 14px;
  padding: 0;
}

.status-bar span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-bar span:first-child {
  font-weight: 600;
  color: #1e293b;
}

/* ---------- Buttons ---------- */
button {
  cursor: pointer;
  border: none;
  border-radius: 10px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  line-height: 1;
  background-color: #f1f5f9;
  color: #1e293b;
}

button:hover {
  background-color: #e2e8f0;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

button.primary {
  background-color: #3b82f6;
  color: #ffffff;
}

button.primary:hover {
  background-color: #2563eb;
  box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3);
}

button.success {
  background-color: #10b981;
  color: #ffffff;
}

button.success:hover {
  background-color: #059669;
  box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.3);
}

button.danger {
  background-color: #ef4444;
  color: #ffffff;
}

button.danger:hover {
  background-color: #dc2626;
  box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.3);
}

button.outline {
  background-color: transparent;
  border: 1px solid #cbd5e1;
  color: #64748b;
}

button.outline:hover {
  background-color: #f8fafc;
  border-color: #94a3b8;
  transform: translateY(-1px);
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

/* ---------- Tables ---------- */
.table-container {
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  overflow-x: auto;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.03);
  margin-top: 8px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  background-color: #f8fafc;
  padding: 14px 20px;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid #e2e8f0;
}

td {
  padding: 14px 20px;
  font-size: 14px;
  color: #1e293b;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

tr:last-child td {
  border-bottom: none;
}

tr:hover td {
  background-color: #f8fafc;
}

tr.total td {
  background-color: #f8fafc;
  font-weight: 600;
  color: #1e293b;
  border-top: 1px solid #e2e8f0;
}

.text-right {
  text-align: right;
}

.text-center {
  text-align: center;
}

.font-mono {
  font-variant-numeric: tabular-nums;
}

/* ---------- Action Buttons (edit/delete) ---------- */
.icon-btn {
  background: transparent !important;
  padding: 6px 10px !important;
  font-size: 16px !important;
  border-radius: 6px !important;
  color: #64748b !important;
  transition: background 0.2s, color 0.2s;
  min-width: 32px;
  min-height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.icon-btn:hover {
  background: #f1f5f9 !important;
  transform: none !important;
  box-shadow: none !important;
}

.icon-btn.danger:hover {
  background: #fef2f2 !important;
  color: #ef4444 !important;
}

/* ---------- Filters ---------- */
.filters {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  flex-wrap: wrap;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
}

.filters label {
  font-size: 13px;
  font-weight: 500;
  color: #475569;
  margin-right: 4px;
}

.filters input[type="date"] {
  padding: 8px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 14px;
  color: #1e293b;
  background-color: #ffffff;
  transition: border-color 0.2s;
}

.filters input[type="date"]:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

/* ---------- Modals (unified) ---------- */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
  padding: 16px;
}

.modal-content {
  background: #ffffff;
  border-radius: 20px;
  padding: 32px;
  width: 440px;
  max-width: 95vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  animation: slideUp 0.3s ease-out;
}

.modal-content h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 24px;
  margin-top: 0;
}

.modal-content label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #475569;
  margin-bottom: 6px;
}

.modal-content select,
.modal-content input[type="number"],
.modal-content input[type="date"],
.modal-content input[type="text"],
.modal-content input[type="password"] {
  width: 100%;
  padding: 10px 14px;
  margin-bottom: 18px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  color: #1e293b;
  transition: all 0.2s;
  background-color: #ffffff;
}

.modal-content select:focus,
.modal-content input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.modal-content .checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
  font-weight: 400;
  font-size: 14px;
  color: #475569;
}

.modal-content .checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: #3b82f6;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.modal-actions button {
  padding: 10px 24px;
}

.modal-actions button:first-child {
  background-color: #3b82f6;
  color: #ffffff;
}

.modal-actions button:first-child:hover {
  background-color: #2563eb;
}

.modal-actions button:last-child {
  background-color: #f1f5f9;
  color: #475569;
}

.modal-actions button:last-child:hover {
  background-color: #e2e8f0;
}

.error {
  color: #ef4444;
  font-size: 14px;
  margin-top: -10px;
  margin-bottom: 10px;
}

/* ---------- Status Badge ---------- */
.status-badge {
  display: inline-block;
  padding: 2px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.planned {
  background-color: #fef3c7;
  color: #d97706;
}

.status-badge.actual {
  background-color: #d1fae5;
  color: #059669;
}

/* ---------- Animations ---------- */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* ---------- Responsive ---------- */
@media (max-width: 1024px) {
  main {
    padding: 20px;
  }
}

@media (max-width: 768px) {
  header {
    padding: 12px 16px;
  }
  header nav {
    gap: 16px;
  }
  header nav a:last-child {
    margin-left: 0;
  }
  .status-bar {
    gap: 16px;
    font-size: 13px;
  }
  main {
    padding: 16px;
  }
  .modal-content {
    padding: 24px;
    width: 100%;
  }
  th, td {
    padding: 10px 14px;
    font-size: 13px;
  }
  .filters {
    flex-direction: column;
    align-items: stretch;
  }
  .filters input[type="date"] {
    width: 100%;
  }
  .actions-cell {
    flex-wrap: wrap;
  }
}

@media (max-width: 640px) {
  .icon-btn {
    padding: 4px 6px !important;
    font-size: 14px !important;
    min-width: 28px;
    min-height: 28px;
  }
  .actions-cell {
    gap: 4px;
  }
}

@media (max-width: 480px) {
  .status-bar {
    font-size: 12px;
    gap: 12px;
  }
  th, td {
    padding: 8px 10px;
    font-size: 12px;
  }
  .modal-content {
    padding: 20px;
  }
  .modal-actions {
    flex-direction: column;
  }
  .modal-actions button {
    width: 100%;
  }
}
</style>