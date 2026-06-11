import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { adminLogin } from '../api/admin';

export const useAdminStore = defineStore('admin', () => {
  const token = ref(localStorage.getItem('admin_token') || '');
  const username = ref(localStorage.getItem('admin_username') || '');
  const role = ref(localStorage.getItem('admin_role') || '');

  const isLoggedIn = computed(() => !!token.value);

  async function login(user: string, password: string) {
    const res = await adminLogin({ username: user, password });
    if (res.data.code !== 200 || !res.data.data) {
      throw new Error(res.data.message || '登录失败');
    }
    const data = res.data.data;
    token.value = data.token;
    username.value = data.username;
    role.value = data.role;
    localStorage.setItem('admin_token', data.token);
    localStorage.setItem('admin_username', data.username);
    localStorage.setItem('admin_role', data.role);
  }

  function logout() {
    token.value = '';
    username.value = '';
    role.value = '';
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_username');
    localStorage.removeItem('admin_role');
  }

  return { token, username, role, isLoggedIn, login, logout };
});
