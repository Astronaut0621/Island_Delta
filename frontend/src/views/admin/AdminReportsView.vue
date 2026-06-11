<template>
  <div class="admin-reports">
    <h2>举报处理</h2>

    <div class="filters">
      <n-select
        v-model:value="filterStatus"
        :options="statusOptions"
        placeholder="按状态筛选"
        clearable
        style="width: 160px"
      />
      <n-button type="primary" @click="loadReports">查询</n-button>
    </div>

    <n-data-table
      :columns="columns"
      :data="reports"
      :loading="loading"
      :pagination="pagination"
      :row-key="(row: any) => row.id"
      @update:page="handlePageChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, h } from 'vue';
import { NSelect, NButton, NDataTable, NTag, useMessage, useDialog } from 'naive-ui';
import { getAdminReports, handleReport, ignoreReport } from '../../api/admin';

const message = useMessage();
const dialog = useDialog();

const loading = ref(false);
const reports = ref<any[]>([]);
const filterStatus = ref<string | null>(null);

const statusOptions = [
  { label: '待处理', value: 'pending' },
  { label: '已处理', value: 'handled' },
  { label: '已忽略', value: 'ignored' },
];

const pagination = reactive({ page: 1, pageSize: 20, itemCount: 0 });

const columns = [
  { title: 'ID', key: 'id', width: 70 },
  { title: '举报原因', key: 'reason', width: 120 },
  { title: '补充说明', key: 'detail', ellipsis: { tooltip: true } },
  { title: '被举报内容', key: 'postContent', ellipsis: { tooltip: true } },
  { title: '内容情绪', key: 'postEmotionType', width: 100 },
  { title: '内容状态', key: 'postStatus', width: 90, render: (row: any) => h(NTag, { size: 'small', type: row.postStatus === 'hidden' ? 'info' : 'success' }, () => row.postStatus || '-') },
  {
    title: '状态', key: 'status', width: 90,
    render: (row: any) => h(NTag, {
      type: row.status === 'pending' ? 'warning' : row.status === 'handled' ? 'success' : 'default',
      size: 'small',
    }, () => row.status),
  },
  {
    title: '操作', key: 'actions', width: 160,
    render: (row: any) => row.status === 'pending'
      ? h('div', [
          h(NButton, { size: 'small', type: 'warning', onClick: () => onHandle(row.id) }, () => '处理'),
          h(NButton, { size: 'small', style: 'margin-left:8px', onClick: () => onIgnore(row.id) }, () => '忽略'),
        ])
      : h('span', { style: 'color:#7e8899' }, '已处理'),
  },
];

async function loadReports() {
  loading.value = true;
  try {
    const res = await getAdminReports({
      status: filterStatus.value || undefined,
      page: pagination.page - 1,
      size: pagination.pageSize,
    });
    reports.value = res.data.data.content;
    pagination.itemCount = res.data.data.totalElements;
  } catch {
    message.error('加载失败');
  } finally {
    loading.value = false;
  }
}

function handlePageChange(page: number) {
  pagination.page = page;
  loadReports();
}

async function onHandle(id: number) {
  dialog.warning({
    title: '确认处理',
    content: '处理后，被举报内容将被隐藏。确定处理吗？',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      await handleReport(id);
      message.success('举报已处理');
      loadReports();
    },
  });
}

async function onIgnore(id: number) {
  await ignoreReport(id);
  message.success('举报已忽略');
  loadReports();
}

onMounted(loadReports);
</script>

<style scoped>
.admin-reports h2 { margin: 0 0 20px; color: #e6eaf0; }
.filters { display: flex; gap: 12px; margin-bottom: 16px; }
</style>
