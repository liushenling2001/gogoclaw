<template>
  <!-- 个性化仪表盘 - GitLab 风格 -->
  <div class="dashboard-container animate-fade-in">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">🧪 Chemical LIMS 仪表盘</h1>
      <p class="page-subtitle">实验室信息管理系统 - 个性化工作台</p>
    </div>

    <!-- 统计卡片网格 -->
    <div class="dashboard-grid">
      <!-- 样品总数 -->
      <div class="stat-card">
        <div class="stat-card-header">
          <div>
            <div class="stat-card-value">1,284</div>
            <div class="stat-card-label">样品总数</div>
          </div>
          <div class="stat-card-icon primary">📊</div>
        </div>
        <div class="stat-card-change positive">
          <span>↑ 12%</span>
          <span>较上月</span>
        </div>
      </div>

      <!-- 进行中测试 -->
      <div class="stat-card">
        <div class="stat-card-header">
          <div>
            <div class="stat-card-value">47</div>
            <div class="stat-card-label">进行中测试</div>
          </div>
          <div class="stat-card-icon success">🔬</div>
        </div>
        <div class="stat-card-change positive">
          <span>↑ 5%</span>
          <span>较上周</span>
        </div>
      </div>

      <!-- 待审核报告 -->
      <div class="stat-card">
        <div class="stat-card-header">
          <div>
            <div class="stat-card-value">23</div>
            <div class="stat-card-label">待审核报告</div>
          </div>
          <div class="stat-card-icon warning">📋</div>
        </div>
        <div class="stat-card-change negative">
          <span>↓ 8%</span>
          <span>较上周</span>
        </div>
      </div>

      <!-- 异常样品 -->
      <div class="stat-card">
        <div class="stat-card-header">
          <div>
            <div class="stat-card-value">3</div>
            <div class="stat-card-label">异常样品</div>
          </div>
          <div class="stat-card-icon danger">⚠️</div>
        </div>
        <div class="stat-card-change negative">
          <span>↑ 2</span>
          <span>新增异常</span>
        </div>
      </div>
    </div>

    <!-- 主要内容区 -->
    <div class="content-grid">
      <!-- 最近活动 -->
      <div class="card">
        <div class="card-header">
          <div class="card-header-title">
            <span>🕐 最近活动</span>
            <button class="btn btn-outline btn-sm">查看全部</button>
          </div>
        </div>
        <div class="card-body">
          <div class="activity-list">
            <div class="activity-item">
              <div class="activity-icon success">✓</div>
              <div class="activity-content">
                <div class="activity-message">
                  <strong>样品 S-2024-001</strong> 测试完成
                </div>
                <div class="activity-meta">
                  <span class="activity-author">张三</span>
                  <span class="activity-time">10 分钟前</span>
                </div>
              </div>
            </div>
            <div class="activity-item">
              <div class="activity-icon primary">📝</div>
              <div class="activity-content">
                <div class="activity-message">
                  <strong>报告 R-2024-045</strong> 已提交审核
                </div>
                <div class="activity-meta">
                  <span class="activity-author">李四</span>
                  <span class="activity-time">25 分钟前</span>
                </div>
              </div>
            </div>
            <div class="activity-item">
              <div class="activity-icon warning">⚠️</div>
              <div class="activity-content">
                <div class="activity-message">
                  <strong>样品 S-2024-089</strong> 检测结果异常
                </div>
                <div class="activity-meta">
                  <span class="activity-author">王五</span>
                  <span class="activity-time">1 小时前</span>
                </div>
              </div>
            </div>
            <div class="activity-item">
              <div class="activity-icon info">📥</div>
              <div class="activity-content">
                <div class="activity-message">
                  <strong>新样品 S-2024-128</strong> 已登记
                </div>
                <div class="activity-meta">
                  <span class="activity-author">赵六</span>
                  <span class="activity-time">2 小时前</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 快速操作 -->
      <div class="card">
        <div class="card-header">
          <div class="card-header-title">
            <span>⚡ 快速操作</span>
          </div>
        </div>
        <div class="card-body">
          <div class="quick-actions">
            <button class="quick-action-btn btn btn-primary">
              <span>📝</span>
              <span>登记新样品</span>
            </button>
            <button class="quick-action-btn btn btn-secondary">
              <span>🔬</span>
              <span>开始测试</span>
            </button>
            <button class="quick-action-btn btn btn-secondary">
              <span>📊</span>
              <span>生成报告</span>
            </button>
            <button class="quick-action-btn btn btn-secondary">
              <span>📋</span>
              <span>审核报告</span>
            </button>
            <button class="quick-action-btn btn btn-secondary">
              <span>📈</span>
              <span>数据分析</span>
            </button>
            <button class="quick-action-btn btn btn-secondary">
              <span>⚙️</span>
              <span>系统设置</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 项目进度 -->
      <div class="card full-width">
        <div class="card-header">
          <div class="card-header-title">
            <span>📊 项目进度</span>
            <button class="btn btn-outline btn-sm">管理项目</button>
          </div>
        </div>
        <div class="card-body">
          <div class="project-list">
            <div class="project-item">
              <div class="project-info">
                <div class="project-name">水质分析项目 Q1-2024</div>
                <div class="project-meta">
                  <span class="badge badge-success">进行中</span>
                  <span class="project-progress-text">78%</span>
                </div>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" style="width: 78%"></div>
              </div>
              <div class="project-stats">
                <span>156/200 样品</span>
                <span>截止：2024-03-31</span>
              </div>
            </div>
            <div class="project-item">
              <div class="project-info">
                <div class="project-name">土壤重金属检测</div>
                <div class="project-meta">
                  <span class="badge badge-warning">待审核</span>
                  <span class="project-progress-text">95%</span>
                </div>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" style="width: 95%"></div>
              </div>
              <div class="project-stats">
                <span>95/100 样品</span>
                <span>截止：2024-02-28</span>
              </div>
            </div>
            <div class="project-item">
              <div class="project-info">
                <div class="project-name">食品添加剂筛查</div>
                <div class="project-meta">
                  <span class="badge badge-info">筹备中</span>
                  <span class="project-progress-text">15%</span>
                </div>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" style="width: 15%"></div>
              </div>
              <div class="project-stats">
                <span>12/80 样品</span>
                <span>截止：2024-04-15</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PersonalizedDashboard',
  data() {
    return {
      stats: {
        totalSamples: 1284,
        ongoingTests: 47,
        pendingReports: 23,
        abnormalSamples: 3
      },
      recentActivities: [],
      projects: []
    }
  },
  mounted() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      // 获取实时数据
      console.log('Fetching dashboard data...')
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 24px;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.card-header-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1rem;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  transition: background 0.2s;
}

.activity-item:hover {
  background: #f9fafb;
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
}

.activity-icon.success {
  background: #dcfce7;
  color: #26a641;
}

.activity-icon.primary {
  background: #f5f0ff;
  color: #6c42f5;
}

.activity-icon.warning {
  background: #fef3c7;
  color: #f0ad4e;
}

.activity-icon.info {
  background: #dbeafe;
  color: #428bca;
}

.activity-content {
  flex: 1;
}

.activity-message {
  font-size: 0.9rem;
  color: #1f2937;
  margin-bottom: 4px;
}

.activity-meta {
  display: flex;
  gap: 12px;
  font-size: 0.8rem;
  color: #6b7280;
}

.activity-author {
  font-weight: 500;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.quick-action-btn {
  justify-content: center;
  padding: 12px 16px;
}

.project-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.project-item {
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.project-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.project-name {
  font-weight: 600;
  color: #1f2937;
}

.project-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.project-progress-text {
  font-size: 0.85rem;
  font-weight: 600;
  color: #6b7280;
}

.progress-bar {
  height: 8px;
  background: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6c42f5 0%, #5b33d4 100%);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.project-stats {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: #6b7280;
}

.full-width {
  grid-column: 1 / -1;
}

@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}
</style>
