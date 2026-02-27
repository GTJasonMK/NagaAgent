<script setup lang="ts">
import { Button, InputNumber, Textarea, ToggleSwitch } from 'primevue'
import { ref } from 'vue'
import ConfigItem from '@/components/ConfigItem.vue'

defineProps<{ loading: boolean }>()
const emit = defineEmits<{
  start: [params: { timeLimitMinutes: number, creditLimit: number, wantFriends: boolean, friendDescription?: string }]
}>()

const timeLimit = ref(300)
const creditLimit = ref(1000)
const wantFriends = ref(true)
const friendDescription = ref('')

function onStart() {
  emit('start', {
    timeLimitMinutes: timeLimit.value,
    creditLimit: creditLimit.value,
    wantFriends: wantFriends.value,
    friendDescription: friendDescription.value || undefined,
  })
}
</script>

<template>
  <!-- 时间限制 -->
  <ConfigItem name="时间限制" description="本次旅行的最长时间">
    <InputNumber
      v-model="timeLimit"
      :min="5" :max="720" suffix=" 分钟"
      show-buttons
    />
  </ConfigItem>

  <!-- 积分限制 -->
  <ConfigItem name="积分限制" description="本次旅行最多消耗的积分">
    <InputNumber
      v-model="creditLimit"
      :min="10" :max="10000" suffix=" 积分"
      show-buttons
    />
  </ConfigItem>
  <div class="text-xs text-white/30 -mt-2 pl-1">
    1元 = 100积分，通过 NagaBusiness 计费系统消耗
  </div>

  <div class="border-t border-white/8 my-1" />

  <!-- 社交开关 -->
  <ConfigItem name="想认识朋友吗？" description="允许 Naga 在旅途中与其他 AI 社交互动">
    <ToggleSwitch v-model="wantFriends" />
  </ConfigItem>

  <!-- 交友描述 -->
  <div v-show="wantFriends" class="flex flex-col gap-2">
    <div class="text-white/60 text-xs pl-1">
      想认识什么朋友？
    </div>
    <Textarea
      v-model="friendDescription"
      rows="3"
      class="resize-none"
      placeholder="描述你希望 Naga 认识的朋友类型..."
    />
  </div>

  <!-- 出发按钮 -->
  <div class="flex justify-center mt-2">
    <Button
      label="出发！"
      class="px-8!"
      :loading="loading"
      @click="onStart"
    />
  </div>
</template>
