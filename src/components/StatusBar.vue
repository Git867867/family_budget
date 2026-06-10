<template>
  <div class="status-bar">
    <span>{{ user?.full_name || 'Гость' }}</span>
    <span>{{ today }}</span>
    <span>Доход: {{ formatAmount(balance.total_income) }}</span>
    <span>Расход: {{ formatAmount(balance.total_expenses) }}</span>
    <span>План: {{ formatAmount(balance.planned_expenses) }}</span>
    <span>Баланс: {{ formatAmount(balance.balance) }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ balance: Object, user: Object })

const today = computed(() => new Date().toLocaleDateString('ru-RU'))

function formatAmount(val) {
  if (val === undefined || val === null) return '—'
  return new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(val)
}
</script>