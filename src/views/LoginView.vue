<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="app-title">Семейный бюджет</h1>
      <p class="app-subtitle">Управляйте финансами вашей семьи</p>

      <div class="login-buttons">
        <button class="primary" @click="showAdminModal = true">Войти как администратор</button>
        <button class="outline" @click="loginGuest">Войти как гость</button>
        <button class="outline" @click="showActivateModal = true">Активировать сеанс члена семьи</button>
      </div>
    </div>

    <!-- Admin Login Modal -->
    <div v-if="showAdminModal" class="modal-overlay" @click.self="showAdminModal = false">
      <div class="modal-content">
        <h3>Вход администратора</h3>
        <label>Логин</label>
        <input v-model="adminUser" placeholder="admin" type="text" />
        <label>Пароль</label>
        <input v-model="adminPass" type="password" placeholder="••••••••" />
        <p v-if="error" class="error">{{ error }}</p>
        <div class="modal-actions">
          <button class="primary" @click="doAdminLogin">Войти</button>
          <button class="outline" @click="showAdminModal = false">Отмена</button>
        </div>
      </div>
    </div>

    <!-- Activate Member Modal -->
    <div v-if="showActivateModal" class="modal-overlay" @click.self="showActivateModal = false">
      <div class="modal-content">
        <h3>Выберите члена семьи</h3>
        <label>Член семьи</label>
        <select v-model="selectedMemberId">
          <option disabled value="">— выберите —</option>
          <option v-for="m in members" :key="m.id" :value="m.id">
            {{ m.full_name }} ({{ m.kinship_type }})
          </option>
        </select>
        <p v-if="error" class="error">{{ error }}</p>
        <div class="modal-actions">
          <button class="primary" @click="activateSession">Активировать</button>
          <button class="outline" @click="showActivateModal = false">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const emit = defineEmits(['login'])

const members = ref([])
const selectedMemberId = ref('')
const showActivateModal = ref(false)
const showAdminModal = ref(false)
const adminUser = ref('')
const adminPass = ref('')
const error = ref('')

onMounted(async () => {
  try {
    const res = await api.get('/public/members')
    members.value = res.data
  } catch (e) {}
})

const loginGuest = async () => {
  try {
    const res = await api.post('/login/guest')
    localStorage.setItem('token', res.data.token)
    emit('login', { full_name: 'Гость', role: 'guest' })
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка сервера'
  }
}

const doAdminLogin = async () => {
  if (!adminUser.value || !adminPass.value) {
    error.value = 'Заполните все поля'
    return
  }
  try {
    const res = await api.post('/login/admin', {
      username: adminUser.value,
      password: adminPass.value
    })
    localStorage.setItem('token', res.data.token)
    emit('login', { full_name: 'Администратор', role: 'admin' })
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Неверные учётные данные'
  }
}

const activateSession = async () => {
  if (!selectedMemberId.value) {
    error.value = 'Выберите члена семьи'
    return
  }
  try {
    const res = await api.post('/session/activate', {
      member_id: parseInt(selectedMemberId.value)
    })
    localStorage.setItem('token', res.data.token)
    emit('login', { full_name: res.data.full_name, role: 'client', member_id: selectedMemberId.value })
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка активации'
  }
}
</script>

<style scoped>
.login-container {
  min-height: 80vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
}

.login-card {
  background: #ffffff;
  padding: 48px;
  border-radius: 24px;
  width: 100%;
  max-width: 420px;
  text-align: center;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  border: 1px solid #e2e8f0;
}

.app-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px;
}

.app-subtitle {
  color: #64748b;
  font-size: 16px;
  margin: 0 0 32px;
}

.login-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.login-buttons button {
  width: 100%;
  padding: 12px;
}
</style>