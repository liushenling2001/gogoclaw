import { createRouter, createWebHistory } from 'vue-router'
import ChemicalsPage from '@/views/ChemicalsPage.vue'
import ExperimentsPage from '@/views/ExperimentsPage.vue'
import ExperimentForm from '@/views/ExperimentForm.vue'
import ExperimentDetail from '@/views/ExperimentDetail.vue'

const routes = [
  {
    path: '/',
    redirect: '/chemicals'
  },
  {
    path: '/chemicals',
    name: 'Chemicals',
    component: ChemicalsPage,
    meta: { title: '化学品管理' }
  },
  {
    path: '/experiments',
    name: 'Experiments',
    component: ExperimentsPage,
    meta: { title: '实验记录' }
  },
  {
    path: '/experiments/new',
    name: 'NewExperiment',
    component: ExperimentForm,
    meta: { title: '新建实验' }
  },
  {
    path: '/experiments/:id',
    name: 'ExperimentDetail',
    component: ExperimentDetail,
    meta: { title: '实验详情' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - LIMS Lite` : 'LIMS Lite'
  next()
})

export default router
