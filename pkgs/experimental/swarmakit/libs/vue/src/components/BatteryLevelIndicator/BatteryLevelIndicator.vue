<template>
  <div class="battery-container" role="progressbar" aria-valuemin="0" aria-valuemax="100" :aria-valuenow="level">
    <div :class="['battery', batteryState]" :style="{ width: `${level}%` }"></div>
    <div v-if="charging" class="charging-icon">⚡</div>
  </div>
</template>

<script lang="ts">
import { defineComponent,computed } from 'vue';

export default defineComponent({
  name: 'BatteryLevelIndicator',
  props: {
    level: {
      type: Number,
      required: true,
    },
    charging: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const batteryState = computed(() => {
      if (props.charging) return 'charging';
      if (props.level > 80) return 'full';
      if (props.level > 20) return 'low';
      return 'critical';
    });

    return { batteryState };
  },
});
</script>

<style scoped lang="css">
.battery-container {
  display: flex;
  align-items: center;
  width: var(--battery-width, 200px);
  height: var(--battery-height, 20px);
  border: 2px solid var(--battery-border-color, #000);
  border-radius: var(--battery-border-radius, 5px);
  position: relative;
  background-color: var(--battery-bg-color, #e0e0e0);
}

.battery {
  height: 100%;
  transition: width 0.3s ease;
}

.charging {
  background-color: var(--charging-bg-color, #00ff00);
}

.full {
  background-color: var(--full-bg-color, #007bff);
}

.low {
  background-color: var(--low-bg-color, #ffff00);
}

.critical {
  background-color: var(--critical-bg-color, #ff0000);
}

.charging-icon {
  position: absolute;
  right: 5px;
  font-size: var(--charging-icon-size, 16px);
  color: var(--charging-icon-color, #ff0);
}
</style>