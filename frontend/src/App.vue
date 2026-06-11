<script setup lang="ts">
import { NConfigProvider, NMessageProvider, NDialogProvider, zhCN, darkTheme } from 'naive-ui';
</script>

<template>
  <n-config-provider :locale="zhCN" :theme="darkTheme">
    <n-message-provider>
      <n-dialog-provider>
        <RouterView />
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>
