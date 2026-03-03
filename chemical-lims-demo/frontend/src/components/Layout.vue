<template>
  <el-container class="layout-container">
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <el-icon><Flask /></el-icon>
        <span>LIMS Lite</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
        router
      >
        <el-menu-item index="/chemicals">
          <el-icon><Van /></el-icon>
          <span>化学品管理</span>
        </el-menu-item>
        <el-menu-item index="/experiments">
          <el-icon><OfficeBuilding /></el-icon>
          <span>实验记录</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-content">
          <h2>{{ currentPageTitle }}</h2>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const currentPageTitle = computed(() => {
  return route.meta.title || 'LIMS Lite'
})

const activeMenu = computed(() => {
  return route.path
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  color: #fff;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
  font-size: 18px;
  font-weight: bold;
  color: #409eff;
  gap: 8px;
  border-bottom: 1px solid #4a5568;
}

.logo .el-icon {
  font-size: 24px;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.header-content h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.main-content {
  background-color: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}
</style>
