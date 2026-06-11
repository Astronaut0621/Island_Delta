<template>
  <div class="admin-posts">
    <h2>情绪内容审核</h2>

    <!-- Filters -->
    <div class="filters">
      <n-select
        v-model:value="filters.status"
        :options="statusOptions"
        placeholder="按状态筛选"
        clearable
        style="width: 160px"
      />
      <n-select
        v-model:value="filters.emotionType"
        :options="emotionOptions"
        placeholder="按情绪类型"
        clearable
        style="width: 160px"
      />
      <n-button type="primary" @click="loadPosts">查询</n-button>
    </div>

    <!-- Table -->
    <n-data-table
      :columns="columns"
      :data="posts"
      :loading="loading"
      :pagination="pagination"
      :row-key="(row: any) => row.id"
      @update:page="handlePageChange"
    />

    <!-- Detail Modal -->
    <n-modal v-model:show="showDetail">
      <n-card title="情绪详情" style="width: 600px" :bordered="false">
        <template v-if="currentPost">
          <n-descriptions :column="1" label-placement="left" bordered>
            <n-descriptions-item label="ID">{{ currentPost.id }}</n-descriptions-item>
            <n-descriptions-item label="情绪类型">{{ currentPost.emotionType }}</n-descriptions-item>
            <n-descriptions-item label="温度">{{ currentPost.temperature }}℃</n-descriptions-item>
            <n-descriptions-item label="内容">{{ currentPost.content }}</n-descriptions-item>
            <n-descriptions-item label="地点">{{ currentPost.locationName || '-' }}</n-descriptions-item>
            <n-descriptions-item label="状态">
              <n-tag :type="statusTagType(currentPost.status)">{{ currentPost.status }}</n-tag>
            </n-descriptions-item>
            <n-descriptions-item label="举报次数">{{ currentPost.reportCount }}</n-descriptions-item>
            <n-descriptions-item label="创建时间">{{ currentPost.createdAt }}</n-descriptions-item>
          </n-descriptions>
          <div class="detail-actions">
            <n-button v-if="currentPost.status === 'normal'" type="warning" @click="handleHide(currentPost.id)">
              隐藏内容
            </n-button>
            <n-button v-if="currentPost.status === 'hidden'" type="info" @click="handleRestore(currentPost.id)">
              恢复内容
            </n-button>
            <n-button v-if="currentPost.status !== 'deleted'" type="error" @click="handleDelete(currentPost.id)">
              删除内容
            </n-button>
          </div>
        </template>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, h } from 'vue';
import {
  NSelect, NButton, NDataTable, NModal, NCard, NDescriptions,
  NDescriptionsItem, NTag, useMessage, useDialog,
} from 'naive-ui';
import { getAdminPosts, hidePost, restorePost, deletePost } from '../../api/admin';

const message = useMessage();
const dialog = useDialog();

const loading = ref(false);
const posts = ref<any[]>([]);
const showDetail = ref(false);
const currentPost = ref<any>(null);

const filters = reactive({ status: null as string | null, emotionType: null as string | null });

const statusOptions = [
  { label: '正常', value: 'normal' },
  { label: '待审核', value: 'pending' },
  { label: '已隐藏', value: 'hidden' },
  { label: '已删除', value: 'deleted' },
];

const emotionOptions = [
  { label: '孤独 lonely', value: 'lonely' },
  { label: '焦虑 anxious', value: 'anxious' },
  { label: '压力 stressed', value: 'stressed' },
  { label: '疲惫 tired', value: 'tired' },
  { label: '失落 sad', value: 'sad' },
  { label: '平静 calm', value: 'calm' },
  { label: '治愈 healed', value: 'healed' },
  { label: '安心 safe', value: 'safe' },
  { label: '快乐 happy', value: 'happy' },
  { label: '希望 hopeful', value: 'hopeful' },
];

const pagination = reactive({ page: 1, pageSize: 20, itemCount: 0 });

const columns = [
  { title: 'ID', key: 'id', width: 70 },
  { title: '情绪', key: 'emotionType', width: 100 },
  { title: '温度', key: 'temperature', width: 80, render: (row: any) => `${row.temperature}℃` },
  { title: '内容', key: 'content', ellipsis: { tooltip: true } },
  { title: '地点', key: 'locationName', width: 120 },
  {
    title: '状态', key: 'status', width: 90,
    render: (row: any) => h(NTag, { type: statusTagType(row.status), size: 'small' }, () => row.status),
  },
  { title: '举报', key: 'reportCount', width: 60 },
  {
    title: '操作', key: 'actions', width: 200,
    render: (row: any) => h('div', [
      h(NButton, { size: 'small', onClick: () => openDetail(row) }, () => '详情'),
      row.status === 'normal' ? h(NButton, { size: 'small', type: 'warning', style: 'margin-left:8px', onClick: () => handleHide(row.id) }, () => '隐藏') : null,
      row.status === 'hidden' ? h(NButton, { size: 'small', type: 'info', style: 'margin-left:8px', onClick: () => handleRestore(row.id) }, () => '恢复') : null,
      row.status !== 'deleted' ? h(NButton, { size: 'small', type: 'error', style: 'margin-left:8px', onClick: () => handleDelete(row.id) }, () => '删除') : null,
    ].filter(Boolean)),
  },
];

function statusTagType(status: string) {
  if (status === 'normal') return 'success' as const;
  if (status === 'pending') return 'warning' as const;
  if (status === 'hidden') return 'info' as const;
  return 'error' as const;
}

async function loadPosts() {
  loading.value = true;
  try {
    const res = await getAdminPosts({
      status: filters.status || undefined,
      emotionType: filters.emotionType || undefined,
      page: pagination.page - 1,
      size: pagination.pageSize,
    });
    posts.value = res.data.data.content;
    pagination.itemCount = res.data.data.totalElements;
  } catch {
    message.error('加载失败');
  } finally {
    loading.value = false;
  }
}

function handlePageChange(page: number) {
  pagination.page = page;
  loadPosts();
}

function openDetail(post: any) {
  currentPost.value = post;
  showDetail.value = true;
}

async function handleHide(id: number) {
  dialog.warning({
    title: '确认隐藏',
    content: '隐藏后该内容将不在前台展示，确定要隐藏吗？',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      await hidePost(id);
      message.success('已隐藏');
      loadPosts();
    },
  });
}

async function handleRestore(id: number) {
  await restorePost(id);
  message.success('已恢复');
  loadPosts();
}

async function handleDelete(id: number) {
  dialog.error({
    title: '确认删除',
    content: '删除后内容标记为deleted状态，确定吗？',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      await deletePost(id);
      message.success('已删除');
      loadPosts();
    },
  });
}

onMounted(loadPosts);
</script>

<style scoped>
.admin-posts h2 { margin: 0 0 20px; color: #e6eaf0; }
.filters { display: flex; gap: 12px; margin-bottom: 16px; }
.detail-actions { margin-top: 16px; display: flex; gap: 8px; }
</style>
