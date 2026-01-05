<template>
  <div class="travel-handbook-container">
    <a-spin :spinning="loading">
      <div v-if="tripPlan" class="handbook-content">
        <!-- 顶部横幅 -->
        <div class="header-banner">
          <div class="banner-content">
            <h1 class="banner-title">
              <span class="mountain-icon">⛰️</span>
              {{ tripPlan.city }}旅行手册
            </h1>
            <p class="banner-slogan">{{ getSlogan(tripPlan.city) }}</p>
            <div class="banner-date">
              {{ formatDate(tripPlan.start_date) }} - {{ formatDate(tripPlan.end_date) }} | 
              {{ tripPlan.days.length }}天{{ tripPlan.days.length - 1 }}晚
            </div>
          </div>
        </div>

        <!-- 信息卡片区域 -->
        <div class="info-cards-section">
          <!-- 天气信息卡片 -->
          <a-card class="info-card weather-card" :bordered="false">
            <template #title>
              <span class="card-icon">🌤️</span>
              行程天气
            </template>
            <div class="weather-list">
              <div
                v-for="weather in tripPlan.weather_info"
                :key="weather.date"
                class="weather-item"
              >
                <div class="weather-date">{{ formatDateShort(weather.date) }}</div>
                <div class="weather-details">
                  <div class="weather-day-info">
                    <span class="weather-icon">☀️</span>
                    <span class="weather-temp">{{ weather.day_temp }}°C</span>
                    <span class="weather-desc">{{ weather.day_weather }}</span>
                  </div>
                  <div class="weather-night-info">
                    <span class="weather-icon">🌙</span>
                    <span class="weather-temp">{{ weather.night_temp }}°C</span>
                    <span class="weather-desc">{{ weather.night_weather }}</span>
                  </div>
                </div>
              </div>
            </div>
          </a-card>

          <!-- 预算概览卡片 -->
          <a-card v-if="tripPlan.budget" class="info-card budget-card" :bordered="false">
            <template #title>
              <span class="card-icon">💰</span>
              预算概览
            </template>
            <div class="budget-list">
              <div class="budget-item">
                <span class="budget-label">住宿</span>
                <span class="budget-value">¥{{ formatPrice(tripPlan.budget.total_hotels || 0) }}</span>
              </div>
              <div class="budget-item">
                <span class="budget-label">餐饮</span>
                <span class="budget-value">¥{{ formatPrice(tripPlan.budget.total_meals || 0) }}</span>
              </div>
              <div class="budget-item">
                <span class="budget-label">交通</span>
                <span class="budget-value">¥{{ formatPrice(tripPlan.budget.total_transportation || 0) }}</span>
              </div>
              <div class="budget-item">
                <span class="budget-label">景点门票</span>
                <span class="budget-value">¥{{ formatPrice(tripPlan.budget.total_attractions || 0) }}</span>
              </div>
              <div class="budget-total">
                <span class="total-label">总计</span>
                <span class="total-value">¥{{ formatPrice(tripPlan.budget.total || 0) }}</span>
              </div>
            </div>
          </a-card>

          <!-- 住宿信息卡片 -->
          <a-card v-if="allHotels.length > 0" class="info-card hotel-card" :bordered="false">
            <template #title>
              <span class="card-icon">🏨</span>
              住宿信息
              <span v-if="allHotels.length > 1" class="hotel-count">（{{ allHotels.length }} 家）</span>
            </template>
            <div v-if="allHotels.length === 1" class="hotel-info">
              <h3 class="hotel-name">{{ allHotels[0].name }}</h3>
              <p class="hotel-address">{{ allHotels[0].address }}</p>
              <div class="hotel-details">
                <span v-if="allHotels[0].rating" class="hotel-rating">评分: {{ allHotels[0].rating }}</span>
                <span v-if="allHotels[0].price_range" class="hotel-price">价格区间: {{ allHotels[0].price_range }}</span>
              </div>
              <p v-if="allHotels[0].description" class="hotel-desc">{{ allHotels[0].description }}</p>
            </div>
            <a-list
              v-else
              :data-source="allHotels"
              :grid="{ gutter: 16, xs: 1, sm: 1, md: 1 }"
            >
              <template #renderItem="{ item, index }">
                <a-list-item>
                  <div class="hotel-info">
                    <h3 class="hotel-name">
                      {{ item.name }}
                      <span class="hotel-index">（选项 {{ index + 1 }}）</span>
                    </h3>
                    <p class="hotel-address">{{ item.address }}</p>
                    <div class="hotel-details">
                      <span v-if="item.rating" class="hotel-rating">评分: {{ item.rating }}</span>
                      <span v-if="item.price_range" class="hotel-price">价格区间: {{ item.price_range }}</span>
                    </div>
                    <p v-if="item.description" class="hotel-desc">{{ item.description }}</p>
                  </div>
                </a-list-item>
              </template>
            </a-list>
          </a-card>
        </div>

        <!-- 地图展示区域 -->
        <a-card class="map-section-card" :bordered="false">
          <template #title>
            <span class="section-icon">🗺️</span>
            旅行路线地图
          </template>
          <div class="map-wrapper">
            <AmapView
              :center="mapCenter"
              :markers="allMarkers"
              height="500px"
            />
          </div>
        </a-card>

        <!-- 每日行程安排 -->
        <div class="daily-itinerary-section">
          <h2 class="section-title">每日行程安排</h2>
          <div
            v-for="(day, dayIndex) in tripPlan.days"
            :key="dayIndex"
            class="day-section"
          >
            <!-- 日期标题栏 -->
            <div class="day-header">
              <div class="day-title">
                <span class="day-number">第{{ dayIndex + 1 }}天</span>
                <span class="day-name">{{ getDayName(day.description) }}</span>
              </div>
              <div class="day-date">{{ formatDateShort(day.date) }}</div>
            </div>

            <!-- 行程描述 -->
            <div class="day-description">
              <p>{{ day.description }}</p>
              <p class="transportation-info">交通方式: {{ day.transportation }}</p>
            </div>

            <!-- 今日景点 -->
            <div v-if="day.attractions && day.attractions.length > 0" class="attractions-section">
              <h3 class="subsection-title">今日景点</h3>
              <a-row :gutter="[16, 16]">
                <a-col
                  v-for="(attraction, index) in day.attractions"
                  :key="index"
                  :xs="24"
                  :sm="12"
                  :md="8"
                >
                  <a-card class="attraction-card" :bordered="false" hoverable>
                    <div v-if="attraction.image_url" class="attraction-image">
                      <img :src="attraction.image_url" :alt="attraction.name" @error="handleImageError" />
                    </div>
                    <div class="attraction-content">
                      <h4 class="attraction-name">{{ attraction.name }}</h4>
                      <p v-if="attraction.description" class="attraction-desc">{{ attraction.description }}</p>
                      <div class="attraction-details">
                        <p v-if="attraction.opentime" class="attraction-time">
                          <span class="detail-label">开放时间:</span> {{ attraction.opentime }}
                        </p>
                        <p v-if="attraction.address" class="attraction-address">
                          <span class="detail-label">地址:</span> {{ attraction.address }}
                        </p>
                        <p v-if="attraction.ticket_price !== undefined && attraction.ticket_price !== null" class="attraction-price">
                          <span class="detail-label">门票:</span> ¥{{ formatPrice(attraction.ticket_price) }}
                        </p>
                      </div>
                    </div>
                  </a-card>
                </a-col>
              </a-row>
            </div>

            <!-- 今日餐饮 -->
            <div v-if="day.meals && day.meals.length > 0" class="meals-section">
              <h3 class="subsection-title">今日餐饮</h3>
              <div class="meals-list">
                <div
                  v-for="(meal, index) in sortedMeals(day.meals)"
                  :key="index"
                  class="meal-item"
                >
                  <div class="meal-type">{{ getMealTypeName(meal.type) }}</div>
                  <div class="meal-info">
                    <h4 class="meal-name">{{ meal.name }}</h4>
                    <p v-if="meal.description" class="meal-desc">{{ meal.description }}</p>
                    <p v-if="meal.address" class="meal-address">{{ meal.address }}</p>
                    <p v-if="meal.estimated_cost > 0" class="meal-cost">¥{{ formatPrice(meal.estimated_cost) }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 重要旅行建议 -->
        <a-card class="suggestions-card" :bordered="false">
          <template #title>
            <span class="section-icon">💡</span>
            重要旅行建议
          </template>
          <div class="suggestions-content">
            <div v-if="tripPlan.overall_suggestions" class="suggestion-item">
              <span class="suggestion-icon">📋</span>
              <div class="suggestion-text">{{ tripPlan.overall_suggestions }}</div>
            </div>
            <div class="suggestion-item">
              <span class="suggestion-icon">🎫</span>
              <div class="suggestion-text">
                门票信息：请提前了解各景点的门票价格和优惠政策，部分景点可能需要提前预约。
              </div>
            </div>
            <div class="suggestion-item">
              <span class="suggestion-icon">🚗</span>
              <div class="suggestion-text">
                交通建议：建议提前规划好交通路线，注意各景点之间的交通方式和时间。
              </div>
            </div>
            <div class="suggestion-item">
              <span class="suggestion-icon">👕</span>
              <div class="suggestion-text">
                穿衣建议：根据天气情况准备合适的衣物，建议携带雨具和舒适的鞋子。
              </div>
            </div>
            <div class="suggestion-item">
              <span class="suggestion-icon">🗺️</span>
              <div class="suggestion-text">
                行程安排：建议合理安排行程，注意休息，避免过度疲劳。
              </div>
            </div>
            <div class="suggestion-item">
              <span class="suggestion-icon">🍽️</span>
              <div class="suggestion-text">
                餐饮建议：可以尝试当地特色美食，注意饮食卫生，建议携带一些干粮和水。
              </div>
            </div>
          </div>
        </a-card>

        <!-- 底部操作栏 -->
        <div class="footer-actions">
          <a-button @click="goToPlanDetail" size="large">
            <template #icon><FileTextOutlined /></template>
            查看详细计划
          </a-button>
          <a-button type="primary" @click="goBack" size="large">
            <template #icon><ArrowLeftOutlined /></template>
            返回首页
          </a-button>
        </div>

        <!-- 页脚 -->
        <div class="page-footer">
          <p>©{{ new Date().getFullYear() }} {{ tripPlan.city }}旅行手册的专属旅行助手</p>
          <p class="disclaimer">行程信息仅供参考，实际安排请根据天气、体力等实际情况调整。</p>
        </div>
      </div>

      <a-empty v-else description="暂无旅行计划数据" />
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { ArrowLeftOutlined, FileTextOutlined } from '@ant-design/icons-vue'
import type { TripPlan, Location, Meal, Hotel } from '@/types'
import AmapView from '@/components/AmapView.vue'

const router = useRouter()
const loading = ref(false)
const tripPlan = ref<TripPlan | null>(null)

// 计算地图中心点
const mapCenter = computed<Location>(() => {
  if (!tripPlan.value) {
    return { longitude: 116.397428, latitude: 39.90923 }
  }

  const locations: Location[] = []
  
  tripPlan.value.days.forEach((day) => {
    day.attractions?.forEach((attraction) => {
      if (attraction.location) {
        locations.push(attraction.location)
      }
    })
    day.meals?.forEach((meal) => {
      if (meal.location) {
        locations.push(meal.location)
      }
    })
    // 处理酒店位置（支持多个酒店）
    if (day.hotels && Array.isArray(day.hotels)) {
      day.hotels.forEach((hotel) => {
        if (hotel.location) {
          locations.push(hotel.location)
        }
      })
    } else if (day.hotel?.location) {
      locations.push(day.hotel.location)
    }
  })

  if (locations.length === 0) {
    return { longitude: 116.397428, latitude: 39.90923 }
  }

  const avgLng = locations.reduce((sum, loc) => sum + loc.longitude, 0) / locations.length
  const avgLat = locations.reduce((sum, loc) => sum + loc.latitude, 0) / locations.length

  return { longitude: avgLng, latitude: avgLat }
})

// 生成所有标记点，带名称标签
const allMarkers = computed(() => {
  if (!tripPlan.value) return []

  const markers: Array<{
    location: Location
    title: string
    label: string
    content: string
    type: 'attraction' | 'meal' | 'hotel'
  }> = []

  tripPlan.value.days.forEach((day, dayIndex) => {
    // 景点标记
    day.attractions?.forEach((attraction) => {
      if (attraction.location) {
        markers.push({
          location: attraction.location,
          title: attraction.name,
          label: attraction.name,
          content: `
            <div style="padding: 8px; min-width: 200px;">
              <h4 style="margin: 0 0 8px 0; color: #1890ff;">📍 ${attraction.name}</h4>
              <p style="margin: 0 0 4px 0; color: #8c8c8c; font-size: 12px;">${attraction.address || ''}</p>
              <p style="margin: 0; color: #595959; font-size: 12px;">第${dayIndex + 1}天</p>
            </div>
          `,
          type: 'attraction'
        })
      }
    })

    // 餐饮标记
    day.meals?.forEach((meal) => {
      if (meal.location && meal.location.longitude && meal.location.latitude) {
        const mealTypeName = getMealTypeName(meal.type)
        const mealName = meal.name || '未命名餐厅'
        const costText = meal.estimated_cost && meal.estimated_cost > 0 
          ? `<p style="margin: 0 0 4px 0; color: #ff4d4f; font-size: 12px; font-weight: 500;">💰 约¥${formatPrice(meal.estimated_cost)}</p>` 
          : ''
        const addressText = meal.address 
          ? `<p style="margin: 0 0 4px 0; color: #8c8c8c; font-size: 12px;">📍 ${meal.address}</p>` 
          : ''
        markers.push({
          location: meal.location,
          title: mealName,
          label: mealName,
          content: `
            <div style="padding: 8px; min-width: 200px;">
              <h4 style="margin: 0 0 8px 0; color: #52c41a; font-weight: 600;">🍽️ ${mealName}</h4>
              <p style="margin: 0 0 4px 0; color: #8c8c8c; font-size: 12px;">
                <span style="background: #52c41a; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">${mealTypeName}</span>
              </p>
              ${addressText}
              ${costText}
              <p style="margin: 0; color: #595959; font-size: 12px;">第${dayIndex + 1}天</p>
            </div>
          `,
          type: 'meal'
        })
      }
    })

    // 酒店标记（支持多个酒店）
    if (day.hotels && Array.isArray(day.hotels)) {
      day.hotels.forEach((hotel) => {
        if (hotel.location) {
          markers.push({
            location: hotel.location,
            title: hotel.name,
            label: hotel.name,
            content: `
              <div style="padding: 8px; min-width: 200px;">
                <h4 style="margin: 0 0 8px 0; color: #722ed1;">🏨 ${hotel.name}</h4>
                <p style="margin: 0 0 4px 0; color: #8c8c8c; font-size: 12px;">${hotel.address || ''}</p>
                <p style="margin: 0; color: #595959; font-size: 12px;">第${dayIndex + 1}天</p>
              </div>
            `,
            type: 'hotel'
          })
        }
      })
    } else if (day.hotel?.location) {
      markers.push({
        location: day.hotel.location,
        title: day.hotel.name,
        label: day.hotel.name,
        content: `
          <div style="padding: 8px; min-width: 200px;">
            <h4 style="margin: 0 0 8px 0; color: #722ed1;">🏨 ${day.hotel.name}</h4>
            <p style="margin: 0 0 4px 0; color: #8c8c8c; font-size: 12px;">${day.hotel.address || ''}</p>
            <p style="margin: 0; color: #595959; font-size: 12px;">第${dayIndex + 1}天</p>
          </div>
        `,
        type: 'hotel'
      })
    }
  })

  return markers
})

// 获取所有酒店信息
const allHotels = computed(() => {
  if (!tripPlan.value) return []
  const hotels: Hotel[] = []
  for (const day of tripPlan.value.days) {
    // 优先使用 hotels 数组
    if (day.hotels && Array.isArray(day.hotels) && day.hotels.length > 0) {
      hotels.push(...day.hotels)
    } else if (day.hotel) {
      // 向后兼容：单个 hotel
      hotels.push(day.hotel)
    }
  }
  return hotels
})

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
}

const formatDateShort = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

// 格式化价格
const formatPrice = (price: number | string): string => {
  if (price === undefined || price === null) return '0'
  const numPrice = typeof price === 'string' ? parseFloat(price) : price
  if (isNaN(numPrice)) return '0'
  return numPrice.toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
}

// 获取城市标语
const getSlogan = (city: string) => {
  const slogans: Record<string, string> = {
    '北京': '千年古都，现代繁华，一场历史与文化的深度体验',
    '上海': '东方明珠，国际都市，一场现代与传统的完美融合',
    '张家界': '奇峰三千，秀水八百，一场自然奇观的深度体验',
    '杭州': '人间天堂，西湖美景，一场诗意与浪漫的邂逅'
  }
  return slogans[city] || `探索${city}的美丽风光，一场难忘的旅行体验`
}

// 获取日期名称
const getDayName = (description: string) => {
  if (!description) return ''
  // 尝试从描述中提取标题
  const match = description.match(/[：:](.+)/)
  return match ? match[1] : description
}

// 获取餐饮类型名称
const getMealTypeName = (type: string) => {
  const map: Record<string, string> = {
    breakfast: '早餐',
    lunch: '午餐',
    dinner: '晚餐',
    snack: '小食'
  }
  return map[type] || type
}

// 排序餐饮
const sortedMeals = (meals: Meal[]) => {
  const order = ['breakfast', 'lunch', 'dinner', 'snack']
  return [...meals].sort((a, b) => {
    return order.indexOf(a.type) - order.indexOf(b.type)
  })
}

// 处理图片加载错误
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
}

// 验证和清理数据
const validateAndCleanTripPlan = (data: any): TripPlan | null => {
  try {
    if (!data || !data.city) {
      return null
    }

    if (!Array.isArray(data.days)) {
      data.days = []
    }

    if (!Array.isArray(data.weather_info)) {
      data.weather_info = []
    }

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

const goBack = () => {
  router.push({ name: 'Home' })
}

const goToPlanDetail = () => {
  router.push({ name: 'Plan', params: { id: Date.now().toString() } })
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
.travel-handbook-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 0;
}

.handbook-content {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
}

/* 顶部横幅 */
.header-banner {
  background: linear-gradient(135deg, #20b2aa 0%, #17a2b8 100%);
  color: white;
  padding: 40px 30px;
  text-align: center;
}

.banner-content {
  max-width: 1000px;
  margin: 0 auto;
}

.banner-title {
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.mountain-icon {
  font-size: 40px;
}

.banner-slogan {
  font-size: 18px;
  margin: 0 0 16px 0;
  opacity: 0.95;
}

.banner-date {
  font-size: 16px;
  opacity: 0.9;
}

/* 信息卡片区域 */
.info-cards-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  padding: 30px;
}

.info-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-icon {
  font-size: 20px;
  margin-right: 8px;
}

/* 天气卡片 */
.weather-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.weather-item {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.weather-date {
  font-weight: 600;
  margin-bottom: 8px;
  color: #20b2aa;
}

.weather-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.weather-day-info,
.weather-night-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.weather-icon {
  font-size: 16px;
}

.weather-temp {
  font-weight: 600;
  color: #20b2aa;
  min-width: 50px;
}

.weather-desc {
  color: #666;
}

/* 预算卡片 */
.budget-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.budget-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.budget-label {
  color: #666;
}

.budget-value {
  font-weight: 600;
  color: #333;
}

.budget-total {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  margin-top: 8px;
  border-top: 2px solid #20b2aa;
}

.total-label {
  font-size: 18px;
  font-weight: 700;
  color: #20b2aa;
}

.total-value {
  font-size: 24px;
  font-weight: 700;
  color: #20b2aa;
}

/* 酒店卡片 */
.hotel-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hotel-name {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: #333;
}

.hotel-index {
  font-size: 14px;
  color: #8c8c8c;
  font-weight: normal;
}

.hotel-count {
  font-size: 14px;
  color: #8c8c8c;
  font-weight: normal;
  margin-left: 8px;
}

.hotel-address {
  color: #666;
  margin: 0;
}

.hotel-details {
  display: flex;
  gap: 16px;
  font-size: 14px;
}

.hotel-rating,
.hotel-price {
  color: #20b2aa;
}

.hotel-desc {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  margin: 8px 0 0 0;
}

/* 地图区域 */
.map-section-card {
  margin: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-icon {
  font-size: 20px;
  margin-right: 8px;
}

.map-wrapper {
  margin-top: 16px;
}

/* 每日行程区域 */
.daily-itinerary-section {
  padding: 30px;
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin: 0 0 30px 0;
  text-align: center;
}

.day-section {
  margin-bottom: 40px;
  background: #fafafa;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.day-header {
  background: linear-gradient(135deg, #20b2aa 0%, #17a2b8 100%);
  color: white;
  padding: 16px 20px;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.day-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.day-number {
  font-size: 20px;
  font-weight: 700;
}

.day-name {
  font-size: 18px;
}

.day-date {
  font-size: 16px;
  opacity: 0.9;
}

.day-description {
  margin-bottom: 20px;
  line-height: 1.8;
  color: #666;
}

.transportation-info {
  margin-top: 8px;
  color: #20b2aa;
  font-weight: 500;
}

/* 景点区域 */
.attractions-section,
.meals-section {
  margin-top: 24px;
}

.subsection-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #20b2aa;
}

.attraction-card {
  height: 100%;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
}

.attraction-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-4px);
}

.attraction-image {
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: #f0f0f0;
}

.attraction-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.attraction-card:hover .attraction-image img {
  transform: scale(1.1);
}

.attraction-content {
  padding: 16px;
}

.attraction-name {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.attraction-desc {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  margin: 0 0 12px 0;
}

.attraction-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
}

.detail-label {
  color: #999;
  font-weight: 500;
}

.attraction-time,
.attraction-address,
.attraction-price {
  margin: 0;
  color: #666;
}

.attraction-price {
  color: #ff4d4f;
  font-weight: 600;
}

/* 餐饮区域 */
.meals-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.meal-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.meal-type {
  min-width: 60px;
  font-weight: 600;
  color: #20b2aa;
  font-size: 16px;
}

.meal-info {
  flex: 1;
}

.meal-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 6px 0;
}

.meal-desc,
.meal-address {
  color: #666;
  font-size: 14px;
  margin: 4px 0;
  line-height: 1.6;
}

.meal-cost {
  color: #ff4d4f;
  font-weight: 600;
  margin-top: 8px;
}

/* 建议卡片 */
.suggestions-card {
  margin: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.suggestions-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.suggestion-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.suggestion-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.suggestion-text {
  flex: 1;
  color: #666;
  line-height: 1.6;
}

/* 底部操作栏 */
.footer-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 30px;
  border-top: 1px solid #f0f0f0;
}

/* 页脚 */
.page-footer {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  color: #999;
  font-size: 12px;
}

.page-footer p {
  margin: 4px 0;
}

.disclaimer {
  font-size: 11px;
  opacity: 0.8;
}

:deep(.ant-card-head-title) {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

:deep(.ant-card-body) {
  padding: 20px;
}
</style>