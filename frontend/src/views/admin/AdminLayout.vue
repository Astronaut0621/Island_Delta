<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>孤岛温差</h2>
        <span class="role-tag">管理后台</span>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/admin/posts" active-class="active">情绪审核</router-link>
        <router-link to="/admin/reports" active-class="active">举报处理</router-link>
        <router-link to="/admin/statistics" active-class="active">统计后台</router-link>
        <router-link to="/admin/nlp-feedback" active-class="active">NLP 反馈</router-link>
      </nav>
      <div class="sidebar-footer">
        <span>{{ adminStore.username }}</span>
        <n-button size="small" quaternary @click="handleLogout">退出</n-button>
      </div>
    </aside>
    <main class="admin-main">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { NButton } from 'naive-ui';
import { useAdminStore } from '../../stores/admin';

const router = useRouter();
const adminStore = useAdminStore();

function handleLogout() {
  adminStore.logout();
  router.push('/admin/login');
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: #0f172a;
  color: #e6eaf0;
}
.sidebar {
  width: 220px;
  background: #1e293b;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #334155;
}
.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid #334155;
}
.sidebar-header h2 {
  margin: 0;
  font-size: 18px;
  color: #ffb86b;
}
.role-tag {
  font-size: 12px;
  color: #7e8899;
}
.sidebar-nav {
  flex: 1;
  padding: 12px 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.sidebar-nav a {
  display: block;
  padding: 10px 20px;
  color: #aab2c0;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s;
}
.sidebar-nav a:hover {
  background: #334155;
  color: #e6eaf0;
}
.sidebar-nav a.active {
  background: #334155;
  color: #ffb86b;
  border-left: 3px solid #ffb86b;
}
.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid #334155;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
  color: #7e8899;
}
.admin-main {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}
</style>
