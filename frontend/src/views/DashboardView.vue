<template>
  <div class="dashboard-view">
    <h1>Tableau de bord</h1>

    <div v-if="loading" class="loading">Chargement...</div>

    <template v-else>
      <section class="section">
        <h2>Résumé des tâches</h2>
        <StatsChart :data="summaryStats" />
      </section>

      <section class="section">
        <h2>Tâches en retard</h2>
        <div v-if="overdueTasks.length === 0" class="empty-state">
          Aucune tâche en retard
        </div>
        <div v-else class="overdue-list">
          <div v-for="task in overdueTasks" :key="task.id" class="overdue-item">
            <span class="overdue-title">{{ task.title }}</span>
            <span class="overdue-date">Échéance : {{ task.due_date }}</span>
            <span class="overdue-status badge badge-{{ task.status }}">{{ task.status }}</span>
          </div>
        </div>
      </section>

      <section class="section">
        <h2>Tâches par utilisateur</h2>
        <div v-if="userStats.length === 0" class="empty-state">
          Aucune donnée disponible
        </div>
        <table v-else class="data-table">
          <thead>
            <tr>
              <th>Utilisateur</th>
              <th>Nombre de tâches</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in userStats" :key="item.username">
              <td>{{ item.username || 'Non assigné' }}</td>
              <td>{{ item.count || 0 }}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { analyticsApi } from '@/composables/useApi'
import StatsChart from '@/components/StatsChart.vue'

const loading = ref(true)
const summaryStats = ref([])
const overdueTasks = ref([])
const userStats = ref([])

const statusColors = {
  todo: '#64748b',
  in_progress: '#3b82f6',
  done: '#16a34a',
  cancelled: '#dc2626'
}

onMounted(async () => {
  try {
    const [summaryRes, overdueRes, byUserRes] = await Promise.all([
      analyticsApi.get('/api/analytics/summary/'),
      analyticsApi.get('/api/analytics/overdue/'),
      analyticsApi.get('/api/analytics/by-user/')
    ])

    const summary = summaryRes.data
    if (summary && typeof summary === 'object') {
      if (Array.isArray(summary)) {
        summaryStats.value = summary.map(item => ({
          label: item.status || item.label,
          value: item.count || item.value || 0,
          color: statusColors[item.status] || '#64748b'
        }))
      } else {
        summaryStats.value = Object.entries(summary).map(([label, value]) => ({
          label,
          value: typeof value === 'number' ? value : 0,
          color: statusColors[label] || '#64748b'
        }))
      }
    }

    overdueTasks.value = Array.isArray(overdueRes.data) ? overdueRes.data : (overdueRes.data?.results || [])
    userStats.value = Array.isArray(byUserRes.data) ? byUserRes.data : (byUserRes.data?.results || [])
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.dashboard-view h1 {
  font-size: 1.75rem;
  color: #1e293b;
  margin-bottom: 24px;
}

.section {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  padding: 24px;
  margin-bottom: 24px;
}

.section h2 {
  font-size: 1.15rem;
  color: #334155;
  margin-bottom: 16px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #64748b;
}

.empty-state {
  text-align: center;
  padding: 24px;
  color: #94a3b8;
}

.overdue-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.overdue-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: #fef2f2;
  border-radius: 6px;
  border-left: 4px solid #dc2626;
}

.overdue-title {
  font-weight: 600;
  flex: 1;
}

.overdue-date {
  color: #64748b;
  font-size: 0.85rem;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 10px 14px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.data-table th {
  font-weight: 600;
  color: #475569;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.data-table tbody tr:hover {
  background: #f8fafc;
}
</style>
