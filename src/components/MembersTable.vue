<template>
  <div class="members-section">
    <div class="section-header">
      <h3>Члены семьи</h3>
      <button class="outline" @click="$emit('add')">Добавить</button>
    </div>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>ФИО</th>
            <th>Родство</th>
            <th class="text-center">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="member in members" :key="member.id">
            <td>{{ member.full_name }}</td>
            <td>{{ member.kinship_type }}</td>
            <td class="text-center actions-cell">
              <button class="icon-btn" @click="$emit('edit', member)" title="Редактировать">✎</button>
              <button class="icon-btn danger" @click="$emit('delete', member)" title="Удалить">✕</button>
            </td>
          </tr>
          <tr v-if="members.length === 0">
            <td colspan="3" class="text-center">Нет добавленных членов семьи</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
defineProps({ members: Array })
defineEmits(['add', 'edit', 'delete'])
</script>

<style scoped>
.members-section {
  margin-top: 32px;
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  padding: 20px;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}
.actions-cell {
  display: flex;
  gap: 8px;
  justify-content: center;
}
.text-center {
  text-align: center;
}
.icon-btn {
  background: transparent !important;
  padding: 6px 10px !important;
  font-size: 16px !important;
  border-radius: 6px !important;
  color: #64748b !important;
}
.icon-btn.danger:hover {
  background: #fef2f2 !important;
  color: #ef4444 !important;
}
</style>