<template>
  <div class="day-plan-detail">
    <a-card :title="dayPlan.description" :bordered="false" class="day-header-card">
      <a-descriptions :column="2" size="small">
        <a-descriptions-item label="日期">{{ dayPlan.date }}</a-descriptions-item>
        <a-descriptions-item label="交通方式">{{ dayPlan.transportation }}</a-descriptions-item>
        <a-descriptions-item label="住宿类型">{{ dayPlan.accommodation }}</a-descriptions-item>
        <a-descriptions-item label="住宿酒店" v-if="hotelsList.length > 0">
          {{ hotelsList.length === 1 ? hotelsList[0].name : `${hotelsList.length} 家酒店可选` }}
        </a-descriptions-item>
      </a-descriptions>
    </a-card>

    <!-- 天气信息 -->
    <a-card v-if="weatherInfo" title="🌤️ 当日天气" :bordered="false" class="weather-info-card">
      <a-descriptions :column="4" size="small">
        <a-descriptions-item label="白天">
          {{ weatherInfo.day_weather || '未知' }} 
          <span v-if="weatherInfo.day_temp !== undefined && weatherInfo.day_temp !== null">
            {{ weatherInfo.day_temp }}°C
          </span>
        </a-descriptions-item>
        <a-descriptions-item label="夜间">
          {{ weatherInfo.night_weather || '未知' }} 
          <span v-if="weatherInfo.night_temp !== undefined && weatherInfo.night_temp !== null">
            {{ weatherInfo.night_temp }}°C
          </span>
        </a-descriptions-item>
        <a-descriptions-item label="风向">
          {{ weatherInfo.wind_direction || '未知' }}
        </a-descriptions-item>
        <a-descriptions-item label="风力">
          {{ weatherInfo.wind_power || '未知' }}
        </a-descriptions-item>
      </a-descriptions>
    </a-card>

    <!-- 酒店信息 -->
    <a-card v-if="hotelsList.length > 0" title="🏨 住宿信息" :bordered="false" class="hotel-card">
      <a-list
        v-if="hotelsList.length > 1"
        :data-source="hotelsList"
        :grid="{ gutter: 16, xs: 1, sm: 1, md: 1 }"
      >
        <template #renderItem="{ item, index }">
          <a-list-item>
            <a-card class="hotel-item-card" :bordered="false">
              <div class="hotel-item-header">
                <h3 class="hotel-item-title">
                  {{ item.name || '未命名酒店' }}
                  <span v-if="hotelsList.length > 1" class="hotel-index">（选项 {{ index + 1 }}）</span>
                </h3>
              </div>
              <a-descriptions :column="2" size="small">
                <a-descriptions-item v-if="item.type" label="酒店类型">
                  {{ item.type }}
                </a-descriptions-item>
                <a-descriptions-item v-if="item.rating" label="评分">
                  {{ item.rating }}
                </a-descriptions-item>
                <a-descriptions-item v-if="item.address" label="地址" :span="2">
                  {{ item.address }}
                </a-descriptions-item>
                <a-descriptions-item v-if="item.price_range" label="价格范围">
                  {{ item.price_range }}
                </a-descriptions-item>
                <a-descriptions-item v-if="item.estimated_cost !== undefined && item.estimated_cost !== null" label="预估费用">
                  ¥{{ formatPrice(item.estimated_cost) }} / 晚
                </a-descriptions-item>
              </a-descriptions>
              <div v-if="item.location && item.location.longitude && item.location.latitude" class="map-section">
                <AmapView
                  :center="item.location"
                  :markers="[
                    {
                      location: item.location,
                      title: item.name || '酒店',
                      content: `<div style="padding: 8px;"><h4>${item.name || '酒店'}</h4><p>${item.address || ''}</p></div>`
                    }
                  ]"
                  height="300px"
                />
              </div>
            </a-card>
          </a-list-item>
        </template>
      </a-list>
      <!-- 单个酒店时使用原来的展示方式 -->
      <template v-else>
        <a-descriptions :column="2" size="small">
          <a-descriptions-item label="酒店名称">
            {{ hotelsList[0].name || '未命名酒店' }}
          </a-descriptions-item>
          <a-descriptions-item v-if="hotelsList[0].type" label="酒店类型">
            {{ hotelsList[0].type }}
          </a-descriptions-item>
          <a-descriptions-item v-if="hotelsList[0].address" label="地址" :span="2">
            {{ hotelsList[0].address }}
          </a-descriptions-item>
          <a-descriptions-item v-if="hotelsList[0].price_range" label="价格范围">
            {{ hotelsList[0].price_range }}
          </a-descriptions-item>
          <a-descriptions-item v-if="hotelsList[0].rating" label="评分">
            {{ hotelsList[0].rating }}
          </a-descriptions-item>
          <a-descriptions-item v-if="hotelsList[0].estimated_cost !== undefined && hotelsList[0].estimated_cost !== null" label="预估费用">
            ¥{{ formatPrice(hotelsList[0].estimated_cost) }} / 晚
          </a-descriptions-item>
        </a-descriptions>
        <div v-if="hotelsList[0].location && hotelsList[0].location.longitude && hotelsList[0].location.latitude" class="map-section">
          <AmapView
            :center="hotelsList[0].location"
            :markers="[
              {
                location: hotelsList[0].location,
                title: hotelsList[0].name || '酒店',
                content: `<div style="padding: 8px;"><h4>${hotelsList[0].name || '酒店'}</h4><p>${hotelsList[0].address || ''}</p></div>`
              }
            ]"
            height="300px"
          />
        </div>
      </template>
    </a-card>

    <!-- 景点列表 -->
    <a-card title="📍 景点安排" :bordered="false" class="attractions-card">
      <a-empty v-if="!dayPlan.attractions || dayPlan.attractions.length === 0" description="暂无景点安排" />
      <a-list
        v-else
        :data-source="dayPlan.attractions"
        :grid="{ gutter: 16, xs: 1, sm: 1, md: 2 }"
      >
        <template #renderItem="{ item }">
          <a-list-item>
            <a-card class="attraction-card" :bordered="false">
              <!-- 景点图片 -->
              <div v-if="item.image_url" class="attraction-image">
                <img :src="item.image_url" :alt="item.name" @error="handleImageError" />
              </div>
              <div class="attraction-header">
                <h3>{{ item.name || '未命名景点' }}</h3>
                <div v-if="item.rating !== undefined && item.rating !== null" class="rating-container">
                  <a-rate 
                    :value="item.rating" 
                    disabled 
                    allow-half 
                  />
                  <span class="rating-text">{{ formatRating(item.rating) }}</span>
                </div>
              </div>
              <a-descriptions :column="1" size="small" class="attraction-info">
                <a-descriptions-item v-if="item.address" label="地址">
                  {{ item.address }}
                </a-descriptions-item>
                <a-descriptions-item v-if="item.opentime" label="开放时间">
                  {{ item.opentime }}
                </a-descriptions-item>
                <a-descriptions-item v-if="item.ticket_price !== undefined && item.ticket_price !== null" label="门票价格">
                  <span class="price">¥{{ formatPrice(item.ticket_price) }}</span>
                </a-descriptions-item>
                <a-descriptions-item v-if="item.category" label="类别">
                  {{ item.category }}
                </a-descriptions-item>
              </a-descriptions>
              <p v-if="item.description" class="attraction-desc">{{ item.description }}</p>
              <div v-if="item.location && item.location.longitude && item.location.latitude" class="attraction-map">
                <AmapView
                  :center="item.location"
                  :markers="[
                    {
                      location: item.location,
                      title: item.name || '景点',
                      content: `<div style="padding: 8px;"><h4>${item.name || '景点'}</h4><p>${item.address || ''}</p></div>`
                    }
                  ]"
                  height="200px"
                />
              </div>
            </a-card>
          </a-list-item>
        </template>
      </a-list>
    </a-card>

    <!-- 餐饮安排 -->
    <a-card title="🍽️ 餐饮安排" :bordered="false" class="meals-card">
      <a-empty v-if="dayPlan.meals.length === 0" description="暂无餐饮安排" />
      <a-timeline v-else>
        <a-timeline-item
          v-for="meal in sortedMeals"
          :key="meal.type"
          :color="getMealColor(meal.type)"
        >
          <template #dot>
            <span class="meal-icon">{{ getMealIcon(meal.type) }}</span>
          </template>
          <a-card class="meal-card" size="small">
            <div class="meal-header">
              <h4>{{ getMealTypeName(meal.type) }} - {{ meal.name || '未命名餐厅' }}</h4>
              <span class="meal-cost" v-if="meal.estimated_cost !== undefined && meal.estimated_cost !== null && meal.estimated_cost > 0">
                ¥{{ formatPrice(meal.estimated_cost) }}
              </span>
            </div>
            <a-descriptions v-if="meal.address" :column="1" size="small">
              <a-descriptions-item label="地址">{{ meal.address }}</a-descriptions-item>
            </a-descriptions>
            <p v-if="meal.description" class="meal-desc">{{ meal.description }}</p>
            <div v-if="meal.location && meal.location.longitude && meal.location.latitude" class="meal-map">
              <AmapView
                :center="meal.location"
                :markers="[
                  {
                    location: meal.location,
                    title: meal.name || '餐厅',
                    content: `<div style="padding: 8px;"><h4>${meal.name || '餐厅'}</h4><p>${meal.address || ''}</p></div>`
                  }
                ]"
                height="200px"
              />
            </div>
          </a-card>
        </a-timeline-item>
      </a-timeline>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DayPlan, Meal, WeatherInfo } from '@/types'
import AmapView from './AmapView.vue'

interface Props {
  dayPlan: DayPlan
  weatherInfo?: WeatherInfo
}

const props = defineProps<Props>()

const mealOrder = ['breakfast', 'lunch', 'dinner', 'snack']

// 获取所有酒店信息（支持 hotels 数组和 hotel 单个对象）
const hotelsList = computed(() => {
  if (props.dayPlan.hotels && Array.isArray(props.dayPlan.hotels) && props.dayPlan.hotels.length > 0) {
    return props.dayPlan.hotels
  }
  if (props.dayPlan.hotel) {
    return [props.dayPlan.hotel]
  }
  return []
})

const sortedMeals = computed(() => {
  if (!props.dayPlan.meals || props.dayPlan.meals.length === 0) {
    return []
  }
  return [...props.dayPlan.meals].sort((a, b) => {
    return mealOrder.indexOf(a.type) - mealOrder.indexOf(b.type)
  })
})

const getMealTypeName = (type: string) => {
  const map: Record<string, string> = {
    breakfast: '早餐',
    lunch: '午餐',
    dinner: '晚餐',
    snack: '小食'
  }
  return map[type] || type
}

const getMealIcon = (type: string) => {
  const map: Record<string, string> = {
    breakfast: '🌅',
    lunch: '🌞',
    dinner: '🌙',
    snack: '🍰'
  }
  return map[type] || '🍽️'
}

const getMealColor = (type: string) => {
  const map: Record<string, string> = {
    breakfast: 'orange',
    lunch: 'blue',
    dinner: 'purple',
    snack: 'green'
  }
  return map[type] || 'blue'
}

// 格式化价格
const formatPrice = (price: number | string): string => {
  if (price === undefined || price === null) return '0'
  const numPrice = typeof price === 'string' ? parseFloat(price) : price
  if (isNaN(numPrice)) return '0'
  return numPrice.toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
}

// 格式化评分
const formatRating = (rating: number): string => {
  if (rating === undefined || rating === null) return ''
  const numRating = typeof rating === 'string' ? parseFloat(rating) : rating
  if (isNaN(numRating)) return ''
  return numRating.toFixed(1)
}

// 处理图片加载错误
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
}
</script>

<style scoped>
.day-plan-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.day-header-card,
.weather-info-card,
.hotel-card,
.attractions-card,
.meals-card {
  border-radius: 8px;
}

.attraction-card {
  height: 100%;
  border-radius: 8px;
  transition: all 0.3s;
}

.attraction-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.attraction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 8px;
}

.rating-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rating-text {
  font-size: 14px;
  color: #8c8c8c;
  font-weight: 500;
}

.attraction-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1890ff;
}

.attraction-info {
  margin: 12px 0;
}

.price {
  color: #ff4d4f;
  font-weight: 600;
  font-size: 16px;
}

.attraction-desc {
  margin: 12px 0 0 0;
  color: #595959;
  line-height: 1.6;
}

.attraction-map,
.meal-map,
.map-section {
  margin-top: 12px;
}

.attraction-image {
  width: 100%;
  height: 200px;
  margin-bottom: 12px;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f5f5;
}

.attraction-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.meal-card {
  border-radius: 8px;
}

.meal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.meal-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.meal-cost {
  color: #ff4d4f;
  font-weight: 600;
}

.meal-desc {
  margin: 8px 0 0 0;
  color: #595959;
  line-height: 1.6;
}

.meal-icon {
  font-size: 20px;
}

.hotel-item-card {
  margin-bottom: 16px;
  border-radius: 8px;
}

.hotel-item-card:last-child {
  margin-bottom: 0;
}

.hotel-item-header {
  margin-bottom: 12px;
}

.hotel-item-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1890ff;
}

.hotel-index {
  font-size: 14px;
  color: #8c8c8c;
  font-weight: normal;
}

:deep(.ant-descriptions-item-label) {
  font-weight: 500;
  color: #8c8c8c;
}

:deep(.ant-card-head-title) {
  font-size: 16px;
  font-weight: 600;
}
</style>

