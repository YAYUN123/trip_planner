<template>
  <div ref="mapContainer" class="amap-container"></div>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
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
  center: () => ({ longitude: 116.397428, latitude: 39.90923 }),
  markers: () => [],
  height: '400px'
})

const mapContainer = ref<HTMLElement>()
let map: any = null
let AMapInstance: any = null
let markers: any[] = []
let resizeTimer: number | null = null

declare global {
  interface Window {
    _AMapSecurityConfig?: {
      securityJsCode?: string
      serviceHost?: string
    }
  }
}

const getLngLat = (location?: Location) => {
  if (!location) return null

  const longitude = Number(location.longitude)
  const latitude = Number(location.latitude)

  if (!Number.isFinite(longitude) || !Number.isFinite(latitude)) {
    return null
  }

  return [longitude, latitude] as [number, number]
}

const scheduleResize = () => {
  if (!map) return

  if (resizeTimer !== null) {
    window.clearTimeout(resizeTimer)
  }

  resizeTimer = window.setTimeout(() => {
    map?.resize()
    resizeTimer = null
  }, 100)
}

const applySecurityConfig = () => {
  const securityJsCode = import.meta.env.VITE_AMAP_SECURITY_JS_CODE
  const serviceHost = import.meta.env.VITE_AMAP_SERVICE_HOST

  if (!securityJsCode && !serviceHost) {
    return
  }

  window._AMapSecurityConfig = {
    ...(window._AMapSecurityConfig || {}),
    ...(securityJsCode ? { securityJsCode } : {}),
    ...(serviceHost ? { serviceHost } : {})
  }
}

const createMarkerIcon = (color: string, emoji: string): string => {
  const canvas = document.createElement('canvas')
  canvas.width = 40
  canvas.height = 50
  const ctx = canvas.getContext('2d')

  if (!ctx) return ''

  ctx.beginPath()
  ctx.arc(20, 20, 18, 0, 2 * Math.PI)
  ctx.fillStyle = color
  ctx.fill()
  ctx.strokeStyle = '#fff'
  ctx.lineWidth = 2
  ctx.stroke()

  ctx.font = '20px Arial'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(emoji, 20, 20)

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
  await nextTick()

  if (!mapContainer.value || map) return

  try {
    applySecurityConfig()
    AMapInstance = await AMapLoader.load({
      key: import.meta.env.VITE_AMAP_KEY || 'your-amap-key',
      version: '2.0',
      plugins: ['AMap.Marker', 'AMap.InfoWindow', 'AMap.Text']
    })

    const center = getLngLat(props.center) ?? [116.397428, 39.90923]

    map = new AMapInstance.Map(mapContainer.value, {
      zoom: 13,
      center,
      viewMode: '3D',
      resizeEnable: true,
      mapStyle: 'amap://styles/normal'
    })

    if (typeof AMapInstance.TileLayer === 'function') {
      map.add(new AMapInstance.TileLayer())
    }

    map.on?.('complete', scheduleResize)
    updateMarkers()
    scheduleResize()
  } catch (error) {
    console.error('AMap load failed:', error)
  }
}

const updateMarkers = () => {
  if (!map || !AMapInstance) return

  markers.forEach((marker) => {
    map.remove(marker)
  })
  markers = []

  const fitViewMarkers: any[] = []
  const center = getLngLat(props.center) ?? [116.397428, 39.90923]
  const validMarkers = props.markers.filter((item) => getLngLat(item.location))

  if (validMarkers.length === 0) {
    const marker = new AMapInstance.Marker({
      position: center,
      title: 'Current Location'
    })
    map.add(marker)
    markers.push(marker)
    scheduleResize()
    return
  }

  validMarkers.forEach((item) => {
    const position = getLngLat(item.location)
    if (!position) return

    let iconColor = '#1890ff'
    let iconType = '📍'

    if (item.type === 'meal') {
      iconColor = '#52c41a'
      iconType = '🍽️'
    } else if (item.type === 'hotel') {
      iconColor = '#722ed1'
      iconType = '🏨'
    }

    const icon = new AMapInstance.Icon({
      size: new AMapInstance.Size(40, 50),
      image: createMarkerIcon(iconColor, iconType),
      imageSize: new AMapInstance.Size(40, 50),
      imageOffset: new AMapInstance.Pixel(0, 0)
    })

    const marker = new AMapInstance.Marker({
      position,
      title: item.title,
      icon,
      offset: new AMapInstance.Pixel(-20, -50)
    })

    fitViewMarkers.push(marker)

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
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        font-weight: 500;
        pointer-events: none;
      `

      const labelMarker = new AMapInstance.Marker({
        position,
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

  if (fitViewMarkers.length > 1) {
    map.setFitView(fitViewMarkers)
  } else {
    const onlyMarkerCenter = getLngLat(validMarkers[0].location)
    if (onlyMarkerCenter) {
      map.setCenter(onlyMarkerCenter)
    }
  }

  scheduleResize()
}

watch(
  () => [props.center, props.markers],
  async () => {
    if (!map) {
      await initMap()
      return
    }

    const center = getLngLat(props.center)
    if (center) {
      map.setCenter(center)
    }

    updateMarkers()
  },
  { deep: true }
)

watch(
  () => props.height,
  () => {
    scheduleResize()
  }
)

const handleWindowResize = () => {
  scheduleResize()
}

onMounted(() => {
  void initMap()
  window.addEventListener('resize', handleWindowResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleWindowResize)

  if (resizeTimer !== null) {
    window.clearTimeout(resizeTimer)
  }

  if (map) {
    map.destroy()
    map = null
  }

  AMapInstance = null
  markers = []
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