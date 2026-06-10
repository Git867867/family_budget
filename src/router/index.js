import { createRouter, createWebHashHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import ReportView from '../views/ReportView.vue'
import HistoryView from '../views/HistoryView.vue'

const routes = [
  { path: '/', name: 'Login', component: LoginView },
  { path: '/dashboard', name: 'Dashboard', component: DashboardView },
  { path: '/report', name: 'Report', component: ReportView },
  { path: '/history', name: 'History', component: HistoryView },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router