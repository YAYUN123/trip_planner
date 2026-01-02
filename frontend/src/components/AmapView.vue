<template>
  <div ref="mapContainer" class="amap-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import type { Location } from '@/types'

interface Props {
  center?: Location
  markers?: Array<{
    location: Location
    title: string
    content?: string
    type?: 'attraction' | 'meal' | 'hotel'
    label?: string
  }>
  height?: string
}

const props = withDefaults(defineProps<Props>(), {
  center: () => ({ longitude: 116.397428, latitude: 39.90923 }), // 默认北京天安门
  markers: () => [],
  height: '400px'
})

const mapContainer = ref<HTMLElement>()
let map: any = null
let AMapInstance: any = null
let markers: any[] = []

// 创建自定义标记图标
const createMarkerIcon = (color: string, emoji: string): string => {
  const canvas = document.createElement('canvas')
  canvas.width = 40
  canvas.height = 50
  const ctx = canvas.getContext('2d')
  
  if (!ctx) return ''
  
  // 绘制圆形背景
  ctx.beginPath()
  ctx.arc(20, 20, 18, 0, 2 * Math.PI)
  ctx.fillStyle = color
  ctx.fill()
  ctx.strokeStyle = '#fff'
  ctx.lineWidth = 2
  ctx.stroke()
  
  // 绘制emoji（简化处理，实际可以使用图片）
  ctx.font = '20px Arial'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(emoji, 20, 20)
  
  // 绘制底部三角形
  ctx.beginPath()
  ctx.moveTo(20, 36)
  ctx.lineTo(12, 50)
  ctx.lineTo(28, 50)
  ctx.closePath()
  ctx.fillStyle = color
  ctx.fill()
  ctx.strokeStyle = '#fff'
  ctx.lineWidth = 2
  ctx.stroke()
  
  return canvas.toDataURL()
}

const initMap = async () => {
  if (!mapContainer.value) return

  try {
    AMapInstance = await AMapLoader.load({
      key: import.meta.env.VITE_AMAP_KEY || 'your-amap-key', // 需要配置环境变量
      version: '2.0',
      plugins: ['AMap.Marker', 'AMap.InfoWindow', 'AMap.Text']
    })

    map = new AMapInstance.Map(mapContainer.value, {
      zoom: 13,
      center: [props.center.longitude, props.center.latitude],
      viewMode: '3D'
    })

    updateMarkers()
  } catch (error) {
    console.error('高德地图加载失败:', error)
  }
}

const updateMarkers = () => {
  if (!map || !AMapInstance) return

  // 清除旧标记
  markers.forEach((marker) => {
    map.remove(marker)
  })
  markers = []

  // 添加新标记
  if (props.markers.length === 0) {
    // 如果没有标记，只显示中心点
    const marker = new AMapInstance.Marker({
      position: [props.center.longitude, props.center.latitude],
      title: '当前位置'
    })
    map.add(marker)
    markers.push(marker)
  } else {
    // 添加所有标记
    props.markers.forEach((item) => {
      // 根据类型设置不同的图标颜色
      let iconColor = '#1890ff' // 默认蓝色
      let iconType = '📍'
      
      if (item.type === 'attraction') {
        iconColor = '#1890ff' // 蓝色
        iconType = '📍'
      } else if (item.type === 'meal') {
        iconColor = '#52c41a' // 绿色
        iconType = '🍽️'
      } else if (item.type === 'hotel') {
        iconColor = '#722ed1' // 紫色
        iconType = '🏨'
      }

      // 创建自定义图标
      const icon = new AMapInstance.Icon({
        size: new AMapInstance.Size(40, 50),
        image: createMarkerIcon(iconColor, iconType),
        imageSize: new AMapInstance.Size(40, 50),
        imageOffset: new AMapInstance.Pixel(0, 0)
      })

      const marker = new AMapInstance.Marker({
        position: [item.location.longitude, item.location.latitude],
        title: item.title,
        icon: icon,
        offset: new AMapInstance.Pixel(-20, -50)
      })

      // 添加文字标签（使用HTML覆盖物）
      if (item.label || item.title) {
        const labelDiv = document.createElement('div')
        labelDiv.className = 'amap-label'
        labelDiv.innerHTML = item.label || item.title
        labelDiv.style.cssText = `
          padding: 4px 8px;
          background-color: ${iconColor};
          color: #fff;
          border-radius: 4px;
          font-size: 12px;
          white-space: nowrap;
          box-shadow: 0 2px 4px rgba(0,0,0,0.3);
          font-weight: 500;
          pointer-events: none;
        `
        
        const labelMarker = new AMapInstance.Marker({
          position: [item.location.longitude, item.location.latitude],
          content: labelDiv,
          offset: new AMapInstance.Pixel(0, 10),
          zIndex: 100
        })
        map.add(labelMarker)
        markers.push(labelMarker)
      }

      if (item.content) {
        const infoWindow = new AMapInstance.InfoWindow({
          content: item.content
        })
        marker.on('click', () => {
          infoWindow.open(map, marker.getPosition())
        })
      }

      map.add(marker)
      markers.push(marker)
    })

    // 调整视野以包含所有标记
    if (props.markers.length > 1) {
      map.setFitView(markers)
    } else {
      map.setCenter([props.markers[0].location.longitude, props.markers[0].location.latitude])
    }
  }
}

watch(
  () => [props.center, props.markers],
  () => {
    if (map) {
      map.setCenter([props.center.longitude, props.center.latitude])
      updateMarkers()
    }
  },
  { deep: true }
)

onMounted(() => {
  initMap()
})
</script>

<style scoped>
.amap-container {
  width: 100%;
  height: v-bind(height);
  border-radius: 8px;
  overflow: hidden;
}
</style>

