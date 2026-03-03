<template>
  <div class="experiment-form">
    <el-card shadow="never">
      <template #header>
        <span>{{ isEdit ? '编辑实验' : '新建实验' }}</span>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="实验名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入实验名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实验状态" prop="status">
              <el-select v-model="formData.status" placeholder="请选择状态" style="width: 100%">
                <el-option label="进行中" value="in_progress" />
                <el-option label="已完成" value="completed" />
                <el-option label="失败" value="failed" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">实验参数</el-divider>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="温度 (°C)" prop="temperature">
              <el-input-number
                v-model="formData.temperature"
                :precision="1"
                :min="-273.15"
                :max="1000"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="时间 (分钟)" prop="time">
              <el-input-number
                v-model="formData.time"
                :precision="0"
                :min="0"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="压力 (atm)" prop="pressure">
              <el-input-number
                v-model="formData.pressure"
                :precision="2"
                :min="0"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="气氛" prop="atmosphere">
              <el-select v-model="formData.atmosphere" placeholder="请选择气氛" style="width: 100%">
                <el-option label="空气" value="air" />
                <el-option label="氮气" value="nitrogen" />
                <el-option label="氩气" value="argon" />
                <el-option label="真空" value="vacuum" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="备注" prop="notes">
              <el-input
                v-model="formData.notes"
                placeholder="请输入实验备注"
                type="textarea"
                :rows="2"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">使用的试剂</el-divider>

        <el-table :data="formData.reagents" border stripe>
          <el-table-column label="选择试剂" min-width="200">
            <template #default="{ $index }">
              <el-select
                v-model="formData.reagents[$index].chemical_id"
                placeholder="选择化学品"
                filterable
                style="width: 100%"
                @change="handleChemicalChange($index)"
              >
                <el-option
                  v-for="chem in chemicalList"
                  :key="chem.id"
                  :label="`${chem.name} (CAS: ${chem.cas})`"
                  :value="chem.id"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="用量 (g)" width="120">
            <template #default="{ $index }">
              <el-input-number
                v-model="formData.reagents[$index].amount_used"
                :precision="3"
                :min="0"
                :step="0.1"
                style="width: 100%"
              />
            </template>
          </el-table-column>
          <el-table-column label="单位" width="80">
            <template #default="{ $index }">
              <el-select
                v-model="formData.reagents[$index].unit"
                style="width: 100%"
              >
                <el-option label="g" value="g" />
                <el-option label="ml" value="ml" />
                <el-option label="mmol" value="mmol" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80" fixed="right">
            <template #default="{ $index }">
              <el-button
                type="danger"
                size="small"
                :disabled="formData.reagents.length <= 1"
                @click="removeReagent($index)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div style="margin-top: 10px; text-align: center">
          <el-button @click="addReagent">
            <el-icon><Plus /></el-icon>
            添加试剂
          </el-button>
        </div>

        <el-divider content-position="left">实验结果</el-divider>

        <el-form-item label="产物信息">
          <el-collapse accordion>
            <el-collapse-item title="展开结果录入" name="result">
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-form-item label="产率 (%)" prop="yield_percent">
                    <el-input-number
                      v-model="formData.result.yield_percent"
                      :precision="2"
                      :min="0"
                      :max="100"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="纯度 (%)" prop="purity_percent">
                    <el-input-number
                      v-model="formData.result.purity_percent"
                      :precision="2"
                      :min="0"
                      :max="100"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="外观描述">
                    <el-input
                      v-model="formData.result.appearance"
                      placeholder="如：白色晶体、淡黄色液体等"
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="分析数据">
                <div v-for="(data, index) in formData.result.analysis_data" :key="index" style="margin-bottom: 10px">
                  <el-row :gutter="10" align="middle">
                    <el-col :span="6">
                      <el-select
                        v-model="data.type"
                        placeholder="分析类型"
                        style="width: 100%"
                      >
                        <el-option label="NMR" value="NMR" />
                        <el-option label="IR" value="IR" />
                        <el-option label="MS" value="MS" />
                        <el-option label="HPLC" value="HPLC" />
                        <el-option label="元素分析" value="elemental_analysis" />
                      </el-select>
                    </el-col>
                    <el-col :span="14">
                      <el-input
                        v-model="data.data"
                        placeholder="输入分析数据"
                      />
                    </el-col>
                    <el-col :span="4">
                      <el-button
                        type="danger"
                        size="small"
                        :disabled="formData.result.analysis_data.length <= 1"
                        @click="removeAnalysisData(index)"
                      >
                        删除
                      </el-button>
                    </el-col>
                  </el-row>
                </div>
                <el-button type="primary" ghost @click="addAnalysisData" style="margin-top: 10px">
                  <el-icon><Plus /></el-icon>
                  添加分析数据
                </el-button>
              </el-form-item>

              <el-form-item label="实验笔记">
                <el-input
                  v-model="formData.result.notes"
                  type="textarea"
                  :rows="4"
                  placeholder="记录实验过程中的观察和心得"
                />
              </el-form-item>
            </el-collapse-item>
          </el-collapse>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">提交</el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const formRef = ref(null)
const submitting = ref(false)
const chemicalList = ref([])
const isEdit = ref(false)

const formData = reactive({
  id: null,
  name: '',
  status: 'in_progress',
  temperature: null,
  time: null,
  pressure: null,
  atmosphere: '',
  notes: '',
  reagents: [
    { chemical_id: null, amount_used: null, unit: 'g' }
  ],
  result: {
    yield_percent: null,
    purity_percent: null,
    appearance: '',
    analysis_data: [],
    notes: ''
  }
})

const rules = {
  name: [{ required: true, message: '请输入实验名称', trigger: 'blur' }],
  status: [{ required: true, message: '请选择实验状态', trigger: 'change' }]
}

// 获取化学品列表
const fetchChemicals = async () => {
  try {
    const res = await request.get('/api/chemicals', { params: { page_size: 1000 } })
    chemicalList.value = res.data.items || res.data
  } catch (error) {
    console.error('获取化学品列表失败:', error)
  }
}

// 加载实验详情（编辑模式）
const loadExperiment = async (id) => {
  try {
    const res = await request.get(`/api/experiments/${id}`)
    const exp = res.data
    Object.assign(formData, {
      ...exp,
      reagents: exp.reagents || [{ chemical_id: null, amount_used: null, unit: 'g' }],
      result: exp.result || {
        yield_percent: null,
        purity_percent: null,
        appearance: '',
        analysis_data: [],
        notes: ''
      }
    })
  } catch (error) {
    console.error('加载实验详情失败:', error)
  }
}

// 添加试剂
const addReagent = () => {
  formData.reagents.push({ chemical_id: null, amount_used: null, unit: 'g' })
}

// 删除试剂
const removeReagent = (index) => {
  formData.reagents.splice(index, 1)
}

// 试剂变化时更新显示名称
const handleChemicalChange = (index) => {
  // 可选：用于更新试剂的详细信息
}

// 添加分析数据
const addAnalysisData = () => {
  formData.result.analysis_data.push({ type: '', data: '' })
}

// 删除分析数据
const removeAnalysisData = (index) => {
  formData.result.analysis_data.splice(index, 1)
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      const url = isEdit.value
        ? `/api/experiments/${formData.id}`
        : '/api/experiments'
      const method = isEdit.value ? 'put' : 'post'
      
      await request[method](url, formData)
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      router.push('/experiments')
    } catch (error) {
      console.error('提交失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

onMounted(async () => {
  await fetchChemicals()
  
  if (route.params.id) {
    isEdit.value = true
    await loadExperiment(route.params.id)
  }
})
</script>

<style scoped>
.experiment-form {
  max-width: 1200px;
  margin: 0 auto;
}

.el-divider--horizontal {
  margin: 20px 0;
}
</style>
