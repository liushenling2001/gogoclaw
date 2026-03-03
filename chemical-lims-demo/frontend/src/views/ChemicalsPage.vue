<template>
  <div class="chemicals-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>化学品列表</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增化学品
          </el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="搜索">
          <el-input
            v-model="searchForm.keyword"
            placeholder="输入名称或 CAS 号搜索"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table
        v-loading="loading"
        :data="chemicalList"
        border
        style="width: 100%"
        stripe
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" min-width="150" />
        <el-table-column prop="cas" label="CAS 号" width="180" />
        <el-table-column prop="molecular_formula" label="分子式" width="120" />
        <el-table-column prop="molecular_weight" label="分子量" width="100" />
        <el-table-column prop="hazard_class" label="危险品分类" width="120">
          <template #default="{ row }">
            <el-tag :type="getHazardType(row.hazard_class)" size="small">
              {{ row.hazard_class || '无' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="storage_conditions" label="存储条件" min-width="150" show-overflow-tooltip />
        <el-table-column prop="stock_quantity" label="库存量 (g)" width="100" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchChemicals"
        @current-change="fetchChemicals"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入化学品名称" />
        </el-form-item>
        <el-form-item label="CAS 号" prop="cas">
          <el-input v-model="formData.cas" placeholder="请输入 CAS 号（如：64-17-5）" />
        </el-form-item>
        <el-form-item label="分子式" prop="molecular_formula">
          <el-input v-model="formData.molecular_formula" placeholder="如：C2H6O" />
        </el-form-item>
        <el-form-item label="分子量" prop="molecular_weight">
          <el-input-number
            v-model="formData.molecular_weight"
            :precision="2"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="危险品分类" prop="hazard_class">
          <el-select v-model="formData.hazard_class" placeholder="请选择" style="width: 100%">
            <el-option label="易燃" value="易燃" />
            <el-option label="易爆" value="易爆" />
            <el-option label="腐蚀性" value="腐蚀性" />
            <el-option label="毒性" value="毒性" />
            <el-option label="氧化性" value="氧化性" />
            <el-option label="无危险" value="无危险" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="存储条件" prop="storage_conditions">
          <el-input
            v-model="formData.storage_conditions"
            placeholder="如：避光、冷藏、密封"
          />
        </el-form-item>
        <el-form-item label="库存量 (g)" prop="stock_quantity">
          <el-input-number
            v-model="formData.stock_quantity"
            :precision="2"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'

const chemicalList = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增化学品')
const formRef = ref(null)
const isEdit = ref(false)

const searchForm = reactive({
  keyword: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const formData = reactive({
  id: null,
  name: '',
  cas: '',
  molecular_formula: '',
  molecular_weight: null,
  hazard_class: '',
  storage_conditions: '',
  stock_quantity: null
})

const rules = {
  name: [{ required: true, message: '请输入化学品名称', trigger: 'blur' }],
  cas: [{ required: true, message: '请输入 CAS 号', trigger: 'blur' }]
}

// 获取化学品列表
const fetchChemicals = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      keyword: searchForm.keyword
    }
    const res = await request.get('/api/chemicals', { params })
    chemicalList.value = res.data.items || res.data
    pagination.total = res.data.total || res.data.length
  } catch (error) {
    console.error('获取化学品列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchChemicals()
}

// 重置搜索
const handleReset = () => {
  searchForm.keyword = ''
  pagination.page = 1
  fetchChemicals()
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增化学品'
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑化学品'
  Object.assign(formData, row)
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      if (isEdit.value) {
        await request.put(`/api/chemicals/${formData.id}`, formData)
        ElMessage.success('更新成功')
      } else {
        await request.post('/api/chemicals', formData)
        ElMessage.success('添加成功')
      }
      dialogVisible.value = false
      fetchChemicals()
    } catch (error) {
      console.error('提交失败:', error)
    }
  })
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除化学品 "${row.name}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      try {
        await request.delete(`/api/chemicals/${row.id}`)
        ElMessage.success('删除成功')
        fetchChemicals()
      } catch (error) {
        console.error('删除失败:', error)
      }
    })
    .catch(() => {})
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  Object.assign(formData, {
    id: null,
    name: '',
    cas: '',
    molecular_formula: '',
    molecular_weight: null,
    hazard_class: '',
    storage_conditions: '',
    stock_quantity: null
  })
}

// 获取危险品标签颜色
const getHazardType = (hazardClass) => {
  const typeMap = {
    '易燃': 'warning',
    '易爆': 'danger',
    '腐蚀性': 'danger',
    '毒性': 'danger',
    '氧化性': 'warning',
    '无危险': 'info',
    '其他': 'info'
  }
  return typeMap[hazardClass] || 'info'
}

onMounted(() => {
  fetchChemicals()
})
</script>

<style scoped>
.chemicals-page {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}
</style>
