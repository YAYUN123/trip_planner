<template>
  <div class="plan-detail-container">
    <a-spin :spinning="loading">
      <div v-if="tripPlan" class="plan-content">
        <!-- 头部信息 -->
        <a-card class="header-card" :bordered="false">
          <div class="header-content">
            <div class="header-left">
              <h1>{{ tripPlan.city }} 旅行计划</h1>
              <p class="date-range">
                {{ tripPlan.start_date }} 至 {{ tripPlan.end_date }}
                <span class="days">（{{ tripPlan.days.length }}天）</span>
              </p>
            </div>
            <a-button type="primary" @click="goBack">
              <template #icon><ArrowLeftOutlined /></template>
              返回首页
            </a-button>
          </div>
        </a-card>

        <!-- 总体建议 -->
        <a-card title="📋 总体建议" class="suggestion-card" :bordered="false">
          <p>{{ tripPlan.overall_suggestions || '暂无总体建议' }}</p>
        </a-card>

        <!-- 预算信息 -->
        <a-card v-if="tripPlan.budget" title="💰 预算明细" class="budget-card" :bordered="false">
          <a-row :gutter="16">
            <a-col :xs="12" :sm="8" :md="4">
              <a-statistic
                title="景点门票"
                :value="tripPlan.budget.total_attractions || 0"
                prefix="¥"
                :precision="0"
              />
            </a-col>
            <a-col :xs="12" :sm="8" :md="4">
              <a-statistic
                title="住宿费用"
                :value="tripPlan.budget.total_hotels || 0"
                prefix="¥"
                :precision="0"
              />
            </a-col>
            <a-col :xs="12" :sm="8" :md="4">
              <a-statistic
                title="餐饮费用"
                :value="tripPlan.budget.total_meals || 0"
                prefix="¥"
                :precision="0"
              />
            </a-col>
            <a-col :xs="12" :sm="8" :md="4">
              <a-statistic
                title="交通费用"
                :value="tripPlan.budget.total_transportation || 0"
                prefix="¥"
                :precision="0"
              />
            </a-col>
            <a-col :xs="24" :sm="24" :md="8">
              <a-statistic
                title="总预算"
                :value="tripPlan.budget.total || 0"
                prefix="¥"
                :precision="0"
                :value-style="{ color: '#1890ff', fontSize: '24px', fontWeight: 'bold' }"
              />
            </a-col>
          </a-row>
        </a-card>

        <!-- 天气信息 -->
        <a-card v-if="tripPlan.weather_info.length > 0" title="🌤️ 天气信息" class="weather-card" :bordered="false">
          <a-row :gutter="16">
            <a-col
              v-for="weather in tripPlan.weather_info"
              :key="weather.date"
              :xs="24"
              :sm="12"
              :md="8"
              :lg="6"
            >
              <a-card class="weather-item" size="small">
                <div class="weather-date">{{ weather.date }}</div>
                <div class="weather-main">
                  <div class="weather-day">
                    <span class="weather-label">白天</span>
                    <span class="weather-temp" v-if="weather.day_temp !== undefined && weather.day_temp !== null">
                      {{ weather.day_temp }}°C
                    </span>
                    <span class="weather-desc">{{ weather.day_weather || '未知' }}</span>
                  </div>
                  <div class="weather-night">
                    <span class="weather-label">夜间</span>
                    <span class="weather-temp" v-if="weather.night_temp !== undefined && weather.night_temp !== null">
                      {{ weather.night_temp }}°C
                    </span>
                    <span class="weather-desc">{{ weather.night_weather || '未知' }}</span>
                  </div>
                  <div class="weather-wind">
                    {{ weather.wind_direction || '未知' }} {{ weather.wind_power || '未知' }}
                  </div>
                </div>
              </a-card>
            </a-col>
          </a-row>
        </a-card>

        <!-- 每日行程 -->
        <a-card title="🗓️ 每日行程" class="days-card" :bordered="false">
          <a-empty v-if="!tripPlan.days || tripPlan.days.length === 0" description="暂无行程安排" />
          <a-tabs v-else v-model:activeKey="activeDay" type="card">
            <a-tab-pane
              v-for="(day, index) in tripPlan.days"
              :key="index"
              :tab="`第${index + 1}天 (${day.date || '日期待定'})`"
            >
              <DayPlanDetail :day-plan="day" :weather-info="getWeatherByDate(day.date)" />
            </a-tab-pane>
          </a-tabs>
        </a-card>
      </div>

      <a-empty v-else description="暂无旅行计划数据" />
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { ArrowLeftOutlined } from '@ant-design/icons-vue'
import type { TripPlan, WeatherInfo } from '@/types'
import DayPlanDetail from '@/components/DayPlanDetail.vue'

const router = useRouter()
const loading = ref(false)
const tripPlan = ref<TripPlan | null>(null)
const activeDay = ref(0)

const goBack = () => {
  router.push({ name: 'Home' })
}

const getWeatherByDate = (date: string): WeatherInfo | undefined => {
  return tripPlan.value?.weather_info.find((w) => w.date === date)
}

// 验证和清理数据
const validateAndCleanTripPlan = (data: any): TripPlan | null => {
  try {
    // 确保必要字段存在
    if (!data || !data.city) {
      return null
    }

    // 确保 days 是数组
    if (!Array.isArray(data.days)) {
      data.days = []
    }

    // 确保 weather_info 是数组
    if (!Array.isArray(data.weather_info)) {
      data.weather_info = []
    }

    // 验证每个 day 的数据结构
    data.days = data.days.map((day: any) => {
      if (!day.attractions || !Array.isArray(day.attractions)) {
        day.attractions = []
      }
      if (!day.meals || !Array.isArray(day.meals)) {
        day.meals = []
      }
      return day
    })

    return data as TripPlan
  } catch (error) {
    console.error('数据验证失败:', error)
    return null
  }
}

onMounted(() => {
  const stored = sessionStorage.getItem('tripPlan')
  if (stored) {
    try {
      const parsed = JSON.parse(stored)
      const validated = validateAndCleanTripPlan(parsed)
      if (validated) {
        tripPlan.value = validated
      } else {
        message.error('旅行计划数据格式不正确')
        router.push({ name: 'Home' })
      }
    } catch (error) {
      message.error('解析旅行计划数据失败')
      console.error(error)
      router.push({ name: 'Home' })
    }
  } else {
    message.warning('未找到旅行计划数据，请返回首页重新生成')
    setTimeout(() => {
      router.push({ name: 'Home' })
    }, 2000)
  }
})
</script>

<style scoped>
.plan-detail-container {
  min-height: 100vh;
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.plan-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.header-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #1890ff;
}

.date-range {
  margin: 0;
  color: #8c8c8c;
  font-size: 16px;
}

.days {
  color: #1890ff;
  font-weight: 500;
}

.suggestion-card,
.budget-card,
.weather-card,
.days-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.suggestion-card p {
  margin: 0;
  line-height: 1.8;
  color: #595959;
}

.weather-item {
  margin-bottom: 16px;
  border-radius: 8px;
}

.weather-date {
  font-weight: 600;
  margin-bottom: 12px;
  color: #1890ff;
}

.weather-main {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.weather-day,
.weather-night {
  display: flex;
  align-items: center;
  gap: 8px;
}

.weather-label {
  width: 40px;
  color: #8c8c8c;
  font-size: 12px;
}

.weather-temp {
  font-weight: 600;
  color: #1890ff;
  min-width: 50px;
}

.weather-desc {
  flex: 1;
  color: #595959;
}

.weather-wind {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 4px;
}

:deep(.ant-tabs-card) {
  background: transparent;
}

:deep(.ant-tabs-card .ant-tabs-tab) {
  border-radius: 8px 8px 0 0;
}

:deep(.ant-card-head-title) {
  font-size: 18px;
  font-weight: 600;
}

:deep(.ant-statistic-title) {
  font-size: 14px;
  color: #8c8c8c;
}
</style>

