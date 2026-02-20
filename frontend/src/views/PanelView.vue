<script setup lang="ts">
import { useWindowSize } from '@vueuse/core'
import { computed } from 'vue'
import { useLink } from 'vue-router'
import brain from '@/assets/icons/brain.png'
import chip from '@/assets/icons/chip.png'
import naga from '@/assets/icons/naga.png'
import toolkit from '@/assets/icons/toolkit.png'
import market from '@/assets/icons/market.svg'
import floatingBall from '@/assets/icons/floating-ball.svg'
import ArkButton from '@/components/ArkButton.vue'
import { useParallax } from '@/composables/useParallax'
import { CONFIG } from '@/utils/config'

const musicBoxIcon = '/assets/Layer 8 (merged).png'

const { height } = useWindowSize()
const scale = computed(() => height.value / 720)

const { rx, ry, tx, ty } = useParallax({ rotateX: 5, rotateY: 4, translateX: 15, translateY: 10, invertRotate: true })

function enterFloating() {
  CONFIG.value.floating.enabled = true
  window.electronAPI?.floating.enter()
}
</script>

<template>
  <div class="flex flex-col items-start justify-center px-1/16">
    <div
      class="grid grid-rows-4 gap-3 *:gap-3 will-change-transform" :style="{
        transformOrigin: 'left',
        transform: `perspective(1000px) rotateX(${rx}deg) rotateY(${8 + ry}deg) translate(${tx}px, ${ty}px) scale(${scale})`,
      }"
    >
      <div class="relative size-full">
        <div class="absolute -left-12 right-1/2 top-2 bottom-2">
          <ArkButton class="size-full bg-#f00! z-1" disabled>
            <div class="size-full">
              娜迦EXE测试版
            </div>
          </ArkButton>
        </div>
        <ArkButton class="size-full" :icon="naga" @click="useLink({ to: '/chat' }).navigate">
          <div class="size-full flex items-center justify-end mr-4em">
            对话
          </div>
        </ArkButton>
      </div>
      <div class="grid grid-cols-2 -translate-x-1/5">
        <ArkButton :icon="brain" title="记忆<br>云海" @click="useLink({ to: '/mind' }).navigate" />
        <ArkButton :icon="toolkit" title="技能<br>工坊" @click="useLink({ to: '/skill' }).navigate" />
      </div>
      <div class="grid grid-cols-2">
        <div class="param-float-group flex">
          <button
            type="button"
            class="float-ball-btn"
            @click="enterFloating"
          >
            <img :src="floatingBall" alt="" class="float-ball-icon">
            <span class="float-ball-text">悬浮球</span>
          </button>
          <div class="param-area flex flex-col flex-1 min-w-0">
            <div class="bg-#363837 text-white p-2 text-sm">
              参数设置
            </div>
            <div class="grow grid grid-cols-2 font-serif font-bold lh-none">
              <ArkButton @click="useLink({ to: '/model' }).navigate">
                <div class="size-full text-lg">模型链接</div>
              </ArkButton>
              <ArkButton @click="useLink({ to: '/memory' }).navigate">
                <div class="size-full text-lg">记忆链接</div>
              </ArkButton>
            </div>
          </div>
        </div>
        <ArkButton :icon="chip" title="终端<br>设置" @click="useLink({ to: '/config' }).navigate" />
      </div>
      <div class="grid grid-cols-2 -translate-x-1/5">
        <ArkButton class="market-btn" :icon="market" title="枢机<br>集市" />
        <ArkButton class="music-btn" :icon="musicBoxIcon" title="音律坊" @click="useLink({ to: '/music' }).navigate" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.market-btn :deep(img),
.music-btn :deep(img) {
  filter: grayscale(1) brightness(0.78) opacity(0.9);
}

.param-float-group {
  background: #363837;
  overflow: hidden;
}

.float-ball-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  gap: 4px;
  padding: 8px 12px;
  width: 56px;
  min-width: 56px;
  background: #363837;
  border: none;
  color: rgba(248, 250, 252, 0.9);
  cursor: pointer;
  transition: background 0.15s;
}

.float-ball-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.float-ball-icon {
  width: 20px;
  height: 20px;
}

.float-ball-text {
  font-size: 1.125rem; /* 与模型链接 text-lg 一致 */
  font-weight: 700;
  font-family: serif;
  line-height: 1.2;
  color: rgba(248, 250, 252, 0.9);
}
</style>
