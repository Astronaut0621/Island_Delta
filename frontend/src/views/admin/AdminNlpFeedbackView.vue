<template>
  <div class="admin-nlp-feedback">
    <h2>NLP 反馈查看</h2>

    <!-- Acceptance Rate -->
    <div class="rate-cards">
      <div class="rate-card">
        <div class="rate-value">{{ acceptanceRate.totalPredictions }}</div>
        <div class="rate-label">预测总数</div>
      </div>
      <div class="rate-card">
        <div class="rate-value">{{ acceptanceRate.correctedCount }}</div>
        <div class="rate-label">修正次数</div>
      </div>
      <div class="rate-card accent">
        <div class="rate-value">{{ acceptanceRate.acceptanceRate?.toFixed(1) }}%</div>
        <div class="rate-label">模型采纳率</div>
      </div>
    </div>

    <!-- Filter -->
    <div class="filters">
      <n-select
        v-model:value="filterCorrected"
        :options="correctedOptions"
        placeholder="筛选类型"
        clearable
        style="width: 160px"
      />
      <n-button type="primary" @click="loadFeedback">查询</n-button>
    </div>

    <!-- Table -->
    <n-data-table
      :columns="columns"
      :data="feedbackList"
      :loading="loading"
      :pagination="pagination"
      :row-key="(row: any) => row.predictionId"
      @update:page="handlePageChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, h } from 'vue';
import { NSelect, NButton, NDataTable, NTag } from 'naive-ui';
import { getNlpFeedback, getNlpAcceptanceRate } from '../../api/admin';

const loading = ref(false);
const feedbackList = ref<any[]>([]);
const filterCorrected = ref<string | null>(null);
const acceptanceRate = ref<any>({});

const correctedOptions = [
  { label: '用户修正过', value: 'true' },
  { label: '直接采纳', value: 'false' },
];

const pagination = reactive({ page: 1, pageSize: 20, itemCount: 0 });

const columns = [
  { title: '预测ID', key: 'predictionId', width: 80 },
  { title: '输入文本', key: 'inputText', ellipsis: { tooltip: true } },
  { title: '模型版本', key: 'modelVersion', width: 140 },
  { title: '预测情绪', key: 'emotionPrediction', width: 100 },
  { title: '预测温度', key: 'temperaturePrediction', width: 90, render: (row: any) => `${row.temperaturePrediction}℃` },
  { title: '安全等级', key: 'safetyPrediction', width: 90, render: (row: any) => h(NTag, { size: 'small', type: row.safetyPrediction === 'crisis' ? 'error' : row.safetyPrediction === 'warning' ? 'warning' : 'success' }, () => row.safetyPrediction || '-') },
  { title: '置信度', key: 'confidence', width: 80 },
  {
    title: '是否修正', key: 'userCorrected', width: 90,
    render: (row: any) => h(NTag, { size: 'small', type: row.userCorrected ? 'warning' : 'success' }, () => row.userCorrected ? '已修正' : '采纳'),
  },
  { title: '修正情绪', key: 'correctedEmotion', width: 100 },
  { title: '修正温度', key: 'correctedTemperature', width: 90, render: (row: any) => row.correctedTemperature != null ? `${row.correctedTemperature}℃` : '-' },
];

async function loadFeedback() {
  loading.value = true;
  try {
    const res = await getNlpFeedback({
      userCorrected: filterCorrected.value === null
        ? undefined
        : filterCorrected.value === 'true',
      page: pagination.page - 1,
      size: pagination.pageSize,
    });
    feedbackList.value = res.data.data.content;
    pagination.itemCount = res.data.data.totalElements;
  } catch {
    // silently fail
  } finally {
    loading.value = false;
  }
}

async function loadAcceptanceRate() {
  try {
    const res = await getNlpAcceptanceRate();
    acceptanceRate.value = res.data.data;
  } catch {
    // silently fail
  }
}

function handlePageChange(page: number) {
  pagination.page = page;
  loadFeedback();
}

onMounted(() => {
  loadFeedback();
  loadAcceptanceRate();
});
</script>

<style scoped>
.admin-nlp-feedback h2 { margin: 0 0 20px; color: #e6eaf0; }
.rate-cards { display: flex; gap: 16px; margin-bottom: 24px; }
.rate-card {
  background: #1e293b; border-radius: 8px; padding: 16px 24px;
  min-width: 140px; border-left: 4px solid #4f8cff;
}
.rate-card.accent { border-left-color: #ffb86b; }
.rate-value { font-size: 24px; font-weight: 600; color: #e6eaf0; }
.rate-label { font-size: 13px; color: #7e8899; margin-top: 4px; }
.filters { display: flex; gap: 12px; margin-bottom: 16px; }
</style>
