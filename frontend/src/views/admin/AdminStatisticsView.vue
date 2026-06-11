<template>
  <div class="admin-statistics">
    <h2>统计后台</h2>

    <!-- Summary Cards -->
    <div class="stat-cards">
      <div class="stat-card">
        <div class="stat-value">{{ stats.totalPosts }}</div>
        <div class="stat-label">总情绪数量</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.todayPosts }}</div>
        <div class="stat-label">今日新增</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.avgTemperature }}℃</div>
        <div class="stat-label">平均温度</div>
      </div>
      <div class="stat-card cold">
        <div class="stat-value">{{ stats.coldestLocation }}</div>
        <div class="stat-label">最冷地点</div>
      </div>
      <div class="stat-card warm">
        <div class="stat-value">{{ stats.warmestLocation }}</div>
        <div class="stat-label">最暖地点</div>
      </div>
    </div>

    <!-- Emotion Tags -->
    <div class="section">
      <h3>高频情绪标签</h3>
      <div v-if="stats.topEmotionTags && stats.topEmotionTags.length > 0" class="tag-list">
        <n-tag v-for="tag in stats.topEmotionTags" :key="tag.emotionType" size="large" style="margin: 4px">
          {{ tag.emotionType }} ({{ tag.count }})
        </n-tag>
      </div>
      <p v-else class="empty">暂无数据</p>
    </div>

    <!-- Recent Trend -->
    <div class="section">
      <h3>最近7天发布趋势</h3>
      <div v-if="stats.recentTrend && stats.recentTrend.length > 0" class="trend-table">
        <n-data-table
          :columns="trendColumns"
          :data="stats.recentTrend"
          :bordered="false"
          size="small"
        />
      </div>
      <p v-else class="empty">暂无数据</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NTag, NDataTable } from 'naive-ui';
import { getAdminStatistics } from '../../api/admin';

const stats = ref<any>({});

const trendColumns = [
  { title: '日期', key: 'date', width: 120 },
  { title: '发布数', key: 'count', width: 100 },
  { title: '平均温度', key: 'avgTemperature', width: 120, render: (row: any) => `${row.avgTemperature}℃` },
];

async function loadStats() {
  try {
    const res = await getAdminStatistics();
    stats.value = res.data.data;
  } catch {
    // silently fail
  }
}

onMounted(loadStats);
</script>

<style scoped>
.admin-statistics h2 { margin: 0 0 20px; color: #e6eaf0; }
.stat-cards {
  display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 24px;
}
.stat-card {
  background: #1e293b; border-radius: 8px; padding: 16px 24px;
  min-width: 150px; border-left: 4px solid #4f8cff;
}
.stat-card.cold { border-left-color: #4f8cff; }
.stat-card.warm { border-left-color: #ffb86b; }
.stat-value { font-size: 24px; font-weight: 600; color: #e6eaf0; }
.stat-label { font-size: 13px; color: #7e8899; margin-top: 4px; }
.section { margin-bottom: 24px; }
.section h3 { margin: 0 0 12px; color: #aab2c0; font-size: 16px; }
.tag-list { display: flex; flex-wrap: wrap; }
.empty { color: #7e8899; }
</style>
