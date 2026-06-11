<template>
  <div class="admin-login">
    <div class="login-card">
      <h1>孤岛温差 · 管理后台</h1>
      <p class="subtitle">管理员登录</p>
      <n-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
        <n-form-item label="用户名" path="username">
          <n-input v-model:value="form.username" placeholder="请输入用户名" />
        </n-form-item>
        <n-form-item label="密码" path="password">
          <n-input
            v-model:value="form.password"
            type="password"
            show-password-on="click"
            placeholder="请输入密码"
          />
        </n-form-item>
        <n-button type="primary" block :loading="loading" attr-type="submit">
          登录
        </n-button>
        <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
      </n-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { NForm, NFormItem, NInput, NButton, useMessage, type FormInst } from 'naive-ui';
import { useAdminStore } from '../../stores/admin';

const router = useRouter();
const message = useMessage();
const adminStore = useAdminStore();

const formRef = ref<FormInst | null>(null);

const loading = ref(false);
const errorMsg = ref('');
const form = reactive({ username: '', password: '' });
const rules = {
  username: { required: true, message: '请输入用户名', trigger: 'blur' },
  password: { required: true, message: '请输入密码', trigger: 'blur' },
};

async function handleLogin() {
  try {
    await formRef.value?.validate();
  } catch {
    return;
  }
  loading.value = true;
  errorMsg.value = '';
  try {
    await adminStore.login(form.username, form.password);
    message.success('登录成功');
    router.push('/admin/posts');
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.message || e?.message || '登录失败，请检查用户名和密码';
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.admin-login {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #101827;
}
.login-card {
  background: #182235;
  border-radius: 12px;
  padding: 40px;
  width: 400px;
  color: #e6eaf0;
}
.login-card h1 {
  font-size: 22px;
  margin: 0 0 4px;
  color: #ffb86b;
}
.subtitle {
  margin: 0 0 24px;
  color: #7e8899;
  font-size: 14px;
}
.error {
  color: #ff7a70;
  margin-top: 12px;
  font-size: 14px;
}
</style>
