<template>
  <div class="home-container">
    <a-card class="form-card" :bordered="false">
      <template #title>
        <div class="title-section">
          <h1>🗺️ 智能旅行规划助手</h1>
          <p class="subtitle">AI驱动的个性化旅行计划生成工具</p>
        </div>
      </template>

      <a-form
        :model="formData"
        :rules="rules"
        layout="vertical"
        @finish="handleSubmit"
        @finishFailed="handleSubmitFailed"
      >
        <a-row :gutter="16">
          <a-col :xs="24" :sm="12">
            <a-form-item name="city" label="目的地城市">
              <a-input
                v-model:value="formData.city"
                placeholder="请输入城市名称，如：北京、上海、杭州"
                size="large"
              />
            </a-form-item>
          </a-col>

          <a-col :xs="24" :sm="12">
            <a-form-item name="travel_days" label="旅行天数">
              <a-input-number
                v-model:value="formData.travel_days"
                :min="1"
                :max="30"
                placeholder="1-30天"
                style="width: 100%"
                size="large"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :xs="24" :sm="12">
            <a-form-item name="start_date" label="开始日期">
              <a-date-picker
                v-model:value="startDate"
                format="YYYY-MM-DD"
                :disabled-date="disabledStartDate"
                placeholder="选择开始日期"
                style="width: 100%"
                size="large"
                @change="handleStartDateChange"
              />
            </a-form-item>
          </a-col>

          <a-col :xs="24" :sm="12">
            <a-form-item name="end_date" label="结束日期">
              <a-date-picker
                v-model:value="endDate"
                format="YYYY-MM-DD"
                :disabled-date="disabledEndDate"
                placeholder="选择结束日期"
                style="width: 100%"
                size="large"
                @change="handleEndDateChange"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :xs="24" :sm="12">
            <a-form-item name="transportation" label="交通方式">
              <a-select
                v-model:value="formData.transportation"
                placeholder="请选择交通方式"
                size="large"
              >
                <a-select-option value="公共交通">公共交通</a-select-option>
                <a-select-option value="自驾">自驾</a-select-option>
                <a-select-option value="出租车">出租车</a-select-option>
                <a-select-option value="步行">步行</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>

          <a-col :xs="24" :sm="12">
            <a-form-item name="accommodation" label="住宿偏好">
              <a-select
                v-model:value="formData.accommodation"
                placeholder="请选择住宿类型"
                size="large"
              >
                <a-select-option value="经济型">经济型</a-select-option>
                <a-select-option value="舒适型">舒适型</a-select-option>
                <a-select-option value="豪华型">豪华型</a-select-option>
                <a-select-option value="民宿">民宿</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item name="preferences" label="旅行偏好（可多选）">
          <a-select
            v-model:value="formData.preferences"
            mode="multiple"
            placeholder="请选择您的旅行偏好"
            size="large"
            :max-tag-count="3"
          >
            <a-select-option value="历史文化">历史文化</a-select-option>
            <a-select-option value="自然风光">自然风光</a-select-option>
            <a-select-option value="美食">美食</a-select-option>
            <a-select-option value="购物">购物</a-select-option>
            <a-select-option value="娱乐">娱乐</a-select-option>
            <a-select-option value="亲子">亲子</a-select-option>
            <a-select-option value="休闲">休闲</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item name="free_text_input" label="额外要求（可选）">
          <a-textarea
            v-model:value="formData.free_text_input"
            :rows="4"
            placeholder="请输入您的特殊要求或偏好，例如：希望避开人群密集的景点、对某类美食有特殊需求等"
            :maxlength="500"
            show-count
          />
        </a-form-item>

        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            size="large"
            :loading="loading"
            block
            class="submit-button"
          >
            {{ loading ? '正在生成您的专属旅行计划...' : '生成旅行计划' }}
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import dayjs, { type Dayjs } from 'dayjs'
import type { TripRequest } from '@/types'
import { createTripPlan } from '@/api'

const router = useRouter()
const loading = ref(false)
const startDate = ref<Dayjs | null>(null)
const endDate = ref<Dayjs | null>(null)

const formData = reactive<TripRequest>({
  city: '',
  start_date: '',
  end_date: '',
  travel_days: 3,
  transportation: '公共交通',
  accommodation: '经济型',
  preferences: [],
  free_text_input: ''
})

const rules = {
  city: [{ required: true, message: '请输入目的地城市', trigger: 'blur' }],
  travel_days: [{ required: true, message: '请输入旅行天数', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }],
  transportation: [{ required: true, message: '请选择交通方式', trigger: 'change' }],
  accommodation: [{ required: true, message: '请选择住宿偏好', trigger: 'change' }]
}

const disabledStartDate = (current: Dayjs) => {
  return current && current < dayjs().startOf('day')
}

const disabledEndDate = (current: Dayjs) => {
  if (!startDate.value) {
    return current && current < dayjs().startOf('day')
  }
  return current && (current < startDate.value || current < dayjs().startOf('day'))
}

const handleStartDateChange = (date: Dayjs | null) => {
  if (date) {
    formData.start_date = date.format('YYYY-MM-DD')
    if (endDate.value && endDate.value < date) {
      endDate.value = null
      formData.end_date = ''
    }
    // 自动计算天数
    if (endDate.value) {
      const days = endDate.value.diff(date, 'day') + 1
      formData.travel_days = days > 0 ? days : 1
    }
  } else {
    formData.start_date = ''
  }
}

const handleEndDateChange = (date: Dayjs | null) => {
  if (date) {
    formData.end_date = date.format('YYYY-MM-DD')
    // 自动计算天数
    if (startDate.value) {
      const days = date.diff(startDate.value, 'day') + 1
      formData.travel_days = days > 0 ? days : 1
    }
  } else {
    formData.end_date = ''
  }
}

const handleSubmit = async () => {
  if (!startDate.value || !endDate.value) {
    message.error('请选择完整的日期范围')
    return
  }

  formData.start_date = startDate.value.format('YYYY-MM-DD')
  formData.end_date = endDate.value.format('YYYY-MM-DD')

  // 验证天数是否匹配
  const calculatedDays = endDate.value.diff(startDate.value, 'day') + 1
  if (calculatedDays !== formData.travel_days) {
    formData.travel_days = calculatedDays
  }

  loading.value = true

  try {
    message.info('正在生成您的专属旅行计划，预计需要5-10分钟，请耐心等待...', 10)
    const tripPlan = await createTripPlan(formData)
    
    // 将结果存储到sessionStorage，然后跳转到地图展示页
    sessionStorage.setItem('tripPlan', JSON.stringify(tripPlan))
    router.push({ name: 'TripMap' })
    
    message.success('旅行计划生成成功！')
  } catch (error: any) {
    message.error(error.message || '生成旅行计划失败，请稍后重试')
    console.error('生成旅行计划失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSubmitFailed = (errorInfo: any) => {
  console.log('表单验证失败:', errorInfo)
  message.error('请填写完整的表单信息')
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  padding: 40px 20px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.form-card {
  max-width: 900px;
  width: 100%;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.title-section {
  text-align: center;
  margin-bottom: 8px;
}

.title-section h1 {
  font-size: 32px;
  font-weight: 600;
  color: #1890ff;
  margin-bottom: 8px;
}

.subtitle {
  color: #8c8c8c;
  font-size: 14px;
  margin: 0;
}

.submit-button {
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  margin-top: 16px;
}

:deep(.ant-card-head-title) {
  font-size: 24px;
}

:deep(.ant-form-item-label > label) {
  font-weight: 500;
}
</style>

