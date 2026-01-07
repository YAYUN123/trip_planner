<template>
  <div class="plan-detail-container">
    <a-spin :spinning="loading">
      <div v-if="tripPlan" class="plan-content" ref="planContentRef">
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
            <div class="header-actions">
              <a-button @click="exportToImage" :loading="exporting">
                <template #icon><DownloadOutlined /></template>
                导出每日计划图片
              </a-button>
              <a-button type="primary" @click="goBack">
                <template #icon><ArrowLeftOutlined /></template>
                返回首页
              </a-button>
            </div>
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
import { ArrowLeftOutlined, DownloadOutlined } from '@ant-design/icons-vue'
import html2canvas from 'html2canvas'
import type { TripPlan, WeatherInfo } from '@/types'
import DayPlanDetail from '@/components/DayPlanDetail.vue'

const router = useRouter()
const loading = ref(false)
const exporting = ref(false)
const tripPlan = ref<TripPlan | null>(null)
const activeDay = ref(0)
const planContentRef = ref<HTMLElement | null>(null)

const goBack = () => {
  router.push({ name: 'Home' })
}

const getWeatherByDate = (date: string): WeatherInfo | undefined => {
  return tripPlan.value?.weather_info.find((w) => w.date === date)
}

// 导出为图片 - 每一天单独导出
const exportToImage = async () => {
  if (!tripPlan.value || !tripPlan.value.days || tripPlan.value.days.length === 0) {
    message.error('没有可导出的行程数据')
    return
  }

  exporting.value = true
  const city = tripPlan.value.city || '旅行计划'
  const days = tripPlan.value.days

  try {
    message.info(`正在生成 ${days.length} 张图片，请稍候...`, 3)
    
    // 创建隐藏的导出容器
    const exportContainer = document.createElement('div')
    exportContainer.style.position = 'fixed'
    exportContainer.style.left = '-9999px'
    exportContainer.style.top = '0'
    exportContainer.style.width = '1400px'
    exportContainer.style.backgroundColor = '#ffffff'
    exportContainer.style.padding = '24px'
    exportContainer.style.boxSizing = 'border-box'
    document.body.appendChild(exportContainer)

    // 依次导出每一天
    for (let dayIndex = 0; dayIndex < days.length; dayIndex++) {
      const day = days[dayIndex]
      const dayNumber = dayIndex + 1
      
      // 创建当天的内容HTML
      const dayHTML = createDayExportHTML(day, dayNumber, city)
      exportContainer.innerHTML = dayHTML
      
      // 等待DOM渲染完成
      await new Promise(resolve => setTimeout(resolve, 300))
      
      // 使用html2canvas导出
      const canvas = await html2canvas(exportContainer, {
        backgroundColor: '#ffffff',
        scale: 2,
        useCORS: true,
        logging: false,
        width: exportContainer.scrollWidth,
        height: exportContainer.scrollHeight,
      })

      // 下载图片
      await new Promise<void>((resolve) => {
        canvas.toBlob((blob) => {
          if (!blob) {
            console.error(`第${dayNumber}天图片生成失败`)
            resolve()
            return
          }

          const url = URL.createObjectURL(blob)
          const link = document.createElement('a')
          const fileName = `${city}-第${dayNumber}天.png`
          
          link.href = url
          link.download = fileName
          link.style.display = 'none'
          
          document.body.appendChild(link)
          link.click()
          
          // 清理
          setTimeout(() => {
            document.body.removeChild(link)
            URL.revokeObjectURL(url)
            resolve()
          }, 100)
        }, 'image/png', 0.95)
      })
      
      // 延迟一下再处理下一张，避免浏览器阻止下载
      if (dayIndex < days.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 500))
      }
    }

    // 清理导出容器
    document.body.removeChild(exportContainer)
    
    message.success(`成功导出 ${days.length} 张图片！`)
    exporting.value = false
    
  } catch (error) {
    console.error('导出图片失败:', error)
    message.error('导出图片失败，请稍后重试')
    exporting.value = false
  }
}

// 创建单天导出的HTML内容
const createDayExportHTML = (day: any, dayNumber: number, city: string) => {
  const weatherInfo = getWeatherByDate(day.date)
  const weatherHTML = weatherInfo ? `
    <div style="margin-bottom: 16px; padding: 16px; background: #f8f9fa; border-radius: 8px;">
      <h3 style="margin: 0 0 12px 0; font-size: 18px; font-weight: 600;">🌤️ 当日天气</h3>
      <div style="display: flex; gap: 16px; flex-wrap: wrap;">
        <div>
          <span style="color: #8c8c8c;">白天：</span>
          <span style="font-weight: 600;">${weatherInfo.day_weather || '未知'}</span>
          ${weatherInfo.day_temp !== undefined && weatherInfo.day_temp !== null ? `<span style="color: #1890ff; margin-left: 8px;">${weatherInfo.day_temp}°C</span>` : ''}
        </div>
        <div>
          <span style="color: #8c8c8c;">夜间：</span>
          <span style="font-weight: 600;">${weatherInfo.night_weather || '未知'}</span>
          ${weatherInfo.night_temp !== undefined && weatherInfo.night_temp !== null ? `<span style="color: #1890ff; margin-left: 8px;">${weatherInfo.night_temp}°C</span>` : ''}
        </div>
        <div>
          <span style="color: #8c8c8c;">风力：</span>
          <span>${weatherInfo.wind_direction || '未知'} ${weatherInfo.wind_power || '未知'}</span>
        </div>
      </div>
    </div>
  ` : ''

  const hotelsList = (day.hotels && Array.isArray(day.hotels) && day.hotels.length > 0) 
    ? day.hotels 
    : (day.hotel ? [day.hotel] : [])
  
  const hotelsHTML = hotelsList.length > 0 ? `
    <div style="margin-bottom: 16px; padding: 16px; background: #f8f9fa; border-radius: 8px;">
      <h3 style="margin: 0 0 12px 0; font-size: 18px; font-weight: 600;">🏨 住宿信息</h3>
      ${hotelsList.map((hotel: any) => `
        <div style="margin-bottom: 12px;">
          <h4 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 600; color: #1890ff;">${hotel.name || '未命名酒店'}</h4>
          ${hotel.address ? `<p style="margin: 4px 0; color: #666;">地址：${hotel.address}</p>` : ''}
          ${hotel.price_range ? `<p style="margin: 4px 0; color: #666;">价格：${hotel.price_range}</p>` : ''}
          ${hotel.rating ? `<p style="margin: 4px 0; color: #666;">评分：${hotel.rating}</p>` : ''}
        </div>
      `).join('')}
    </div>
  ` : ''

  const attractionsHTML = day.attractions && day.attractions.length > 0 ? `
    <div style="margin-bottom: 16px;">
      <h3 style="margin: 0 0 12px 0; font-size: 18px; font-weight: 600;">📍 景点安排</h3>
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
        ${day.attractions.map((attr: any) => `
          <div style="padding: 16px; background: #ffffff; border: 1px solid #e8e8e8; border-radius: 8px;">
            <h4 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 600; color: #1890ff;">${attr.name || '未命名景点'}</h4>
            ${attr.description ? `<p style="margin: 8px 0; color: #666; font-size: 14px; line-height: 1.6;">${attr.description}</p>` : ''}
            ${attr.address ? `<p style="margin: 4px 0; color: #666; font-size: 13px;">地址：${attr.address}</p>` : ''}
            ${attr.opentime ? `<p style="margin: 4px 0; color: #666; font-size: 13px;">开放时间：${attr.opentime}</p>` : ''}
            ${attr.ticket_price !== undefined && attr.ticket_price !== null ? `<p style="margin: 4px 0; color: #ff4d4f; font-weight: 600;">门票：¥${attr.ticket_price}</p>` : ''}
          </div>
        `).join('')}
      </div>
    </div>
  ` : ''

  const mealsHTML = day.meals && day.meals.length > 0 ? `
    <div style="margin-bottom: 16px;">
      <h3 style="margin: 0 0 12px 0; font-size: 18px; font-weight: 600;">🍽️ 餐饮安排</h3>
      <div style="display: flex; flex-direction: column; gap: 12px;">
        ${day.meals.map((meal: any) => {
          const mealTypeMap: Record<string, string> = {
            breakfast: '早餐',
            lunch: '午餐',
            dinner: '晚餐',
            snack: '小食'
          }
          const mealType = mealTypeMap[meal.type] || meal.type
          return `
            <div style="padding: 12px; background: #ffffff; border-left: 4px solid #1890ff; border-radius: 4px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h4 style="margin: 0; font-size: 16px; font-weight: 600;">${mealType} - ${meal.name || '未命名餐厅'}</h4>
                ${meal.estimated_cost !== undefined && meal.estimated_cost !== null && meal.estimated_cost > 0 
                  ? `<span style="color: #ff4d4f; font-weight: 600;">¥${meal.estimated_cost}</span>` 
                  : ''}
              </div>
              ${meal.address ? `<p style="margin: 4px 0; color: #666; font-size: 13px;">地址：${meal.address}</p>` : ''}
              ${meal.description ? `<p style="margin: 8px 0 0 0; color: #666; font-size: 14px; line-height: 1.6;">${meal.description}</p>` : ''}
            </div>
          `
        }).join('')}
      </div>
    </div>
  ` : ''

  return `
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; color: #333;">
      <!-- 头部 -->
      <div style="margin-bottom: 24px; padding: 20px; background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%); border-radius: 12px; color: white;">
        <h1 style="margin: 0 0 8px 0; font-size: 32px; font-weight: 600;">${city} 旅行计划</h1>
        <p style="margin: 0; font-size: 18px; opacity: 0.95;">第${dayNumber}天 - ${day.date || '日期待定'}</p>
        ${day.description ? `<p style="margin: 12px 0 0 0; font-size: 16px; opacity: 0.9;">${day.description}</p>` : ''}
      </div>

      <!-- 行程信息 -->
      <div style="margin-bottom: 16px; padding: 16px; background: #f8f9fa; border-radius: 8px;">
        <div style="display: flex; gap: 24px; flex-wrap: wrap;">
          <div>
            <span style="color: #8c8c8c;">交通方式：</span>
            <span style="font-weight: 600;">${day.transportation || '未指定'}</span>
          </div>
          <div>
            <span style="color: #8c8c8c;">住宿类型：</span>
            <span style="font-weight: 600;">${day.accommodation || '未指定'}</span>
          </div>
        </div>
      </div>

      ${weatherHTML}
      ${hotelsHTML}
      ${attractionsHTML}
      ${mealsHTML}
    </div>
  `
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

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
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

