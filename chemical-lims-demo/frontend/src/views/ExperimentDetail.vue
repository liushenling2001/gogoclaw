<template>
  <div class="experiment-detail">
    <el-card shadow="never" v-if="experiment">
      <template #header>
        <div class="card-header">
          <span>{{ experiment.name }}</span>
          <div>
            <el-button type="primary" @click="$router.push(`/experiments/${experiment.id}/edit`)">
              编辑
            </el-button>
            <el-button @click="$router.back()">返回</el-button>
          </div>
        </div>
      </template>

      <!-- 基本信息 -->
      <el-descriptions :column="2" border>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(experiment.status)">
            {{ getStatusText(experiment.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDate(experiment.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">
          {{ formatDate(experiment.updated_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="气氛">
          {{ getAtmosphereText(experiment.atmosphere) }}
        </el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">实验参数</el-divider>

      <el-row :gutter="20" class="params-row">
        <el-col :span="8">
          <el-card shadow="hover" class="param-card">
            <template #header>
              <span>温度</span>
            </template>
            <div class="param-value">{{ experiment.temperature }}°C</div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" class="param-card">
            <template #header>
              <span>时间</span>
            </template>
            <div class="param-value">{{ experiment.time }}分钟</div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" class="param-card">
            <template #header>
              <span>压力</span>
            </template>
            <div class="param-value">{{ experiment.pressure }}atm</div>
          </el-card>
        </el-col>
      </el-row>

      <el-descriptions v-if="experiment.notes" :column="1" border style="margin-top: 20px">
        <el-descriptions-item label="备注">
          {{ experiment.notes }}
        </el-descriptions-item>
      </el-descriptions>

      <!-- 使用的试剂 -->
      <el-divider content-position="left">使用的试剂</el-divider>

      <el-table :data="experiment.reagents" border stripe>
        <el-table-column prop="chemical_id" label="化学品 ID" width="80" />
        <el-table-column label="名称" min-width="150">
          <template #default="{ row }">
            {{ getChemicalName(row.chemical_id) }}
          </template>
        </el-table-column>
        <el-table-column label="用量" width="120">
          <template #default="{ row }">
            {{ row.amount_used }}{{ row.unit }}
          </template>
        </el-table-column>
        <el-table-column label="单位" width="80">
          <template #default="{ row }">
            {{ row.unit }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 实验结果 -->
      <el-divider content-position="left">实验结果</el-divider>

      <el-card v-if="experiment.result" shadow="never" class="result-card">
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="result-item">
              <span class="label">产率</span>
              <span class="value success">{{ experiment.result.yield_percent }}%</span>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="result-item">
              <span class="label">纯度</span>
              <span class="value success">{{ experiment.result.purity_percent }}%</span>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="result-item">
              <span class="label">外观</span>
              <span class="value">{{ experiment.result.appearance || '-' }}</span>
            </div>
          </el-col>
        </el-row>

        <el-divider v-if="experiment.result.analysis_data?.length" />

        <div v-if="experiment.result.analysis_data?.length" class="analysis-section">
          <h4>分析数据</h4>
          <ul class="analysis-list">
            <li v-for="(item, index) in experiment.result.analysis_data" :key="index">
              <el-tag size="small" type="info">{{ getAnalysisTypeText(item.type) }}</el-tag>
              <span class="data-text">{{ item.data }}</span>
            </li>
          </ul>
        </div>

        <el-divider v-if="experiment.result.notes" />

        <div v-if="experiment.result.notes" class="notes-section">
          <h4>实验笔记</h4>
          <p>{{ experiment.result.notes }}</p>
        </div>
      </el-card>

      <el-alert
        v-else
        title="暂无实验结果"
        description="该实验尚未录入结果数据"
        type="info"
        :closable="false"
        show-icon
      />
    </el-card>

    <el-empty v-else description="实验不存在" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import request from '@/utils/request'

const route = useRoute()
const experiment = ref(null)
const chemicalsCache = ref([])

// 获取实验详情
const loadExperiment = async (id) => {
  try {
    const res = await request.get(`/api/experiments/${id}`)
    experiment.value = res.data
    // 缓存化学品信息用于显示名称
    if (res.data.reagents?.length) {
      const chemIds = [...new Set(res.data.reagents.map(r => r.chemical_id))]
      for (const id of chemIds) {
        try {
          const chemRes = await request.get(`/api/chemicals/${id}`)
          chemicalsCache.value[id] = chemRes.data
        } catch (e) {}
      }
    }
  } catch (error) {
    console.error('加载实验详情失败:', error)
  }
}

// 获取化学品名称
const getChemicalName = (id) => {
  return chemicalsCache.value[id]?.name || `ID: ${id}`
}

// 获取状态文字
const getStatusText = (status) => {
  const statusMap = {
    'in_progress': '进行中',
    'completed': '已完成',
    'failed': '失败'
  }
  return statusMap[status] || status
}

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    'in_progress': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取气氛文字
const getAtmosphereText = (atmosphere) => {
  const atmMap = {
    'air': '空气',
    'nitrogen': '氮气',
    'argon': '氩气',
    'vacuum': '真空',
    'other': '其他'
  }
  return atmMap[atmosphere] || atmosphere
}

// 获取分析类型文字
const getAnalysisTypeText = (type) => {
  const typeMap = {
    'NMR': 'NMR',
    'IR': 'IR',
    'MS': '质谱',
    'HPLC': 'HPLC',
    'elemental_analysis': '元素分析'
  }
  return typeMap[type] || type
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadExperiment(route.params.id)
})
</script>

<style scoped>
.experiment-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.params-row {
  margin-top: 20px;
}

.param-card {
  text-align: center;
}

.param-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.result-card {
  margin-top: 20px;
}

.result-item {
  display: flex;
  flex-direction: column;
  padding: 10px 0;
}

.result-item .label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.result-item .value {
  font-size: 20px;
  font-weight: bold;
}

.result-item .value.success {
  color: #67c23a;
}

.analysis-section {
  margin-top: 15px;
}

.analysis-section h4,
.notes-section h4 {
  font-size: 16px;
  color: #303133;
  margin-bottom: 10px;
}

.analysis-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.analysis-list li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.analysis-list li:last-child {
  border-bottom: none;
}

.analysis-list .data-text {
  flex: 1;
  color: #606266;
  word-break: break-all;
}

.notes-section p {
  color: #606266;
  line-height: 1.8;
  white-space: pre-wrap;
}
</style>
