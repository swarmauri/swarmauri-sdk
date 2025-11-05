<template>
  <div class="fill-tool">
    <button :disabled="isDisabled" @click="toggleActive" :class="{ active: isActive }" aria-label="Fill Tool">
      Fill
    </button>
    <div v-if="isActive" class="fill-options">
      <label for="tolerance">Tolerance:</label>
      <input id="tolerance" type="range" min="0" max="100" v-model="tolerance" />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'FillTool',
  setup() {
    const isActive = ref(false);
    const isDisabled = ref(false);
    const tolerance = ref(50);

    const toggleActive = () => {
      if (!isDisabled.value) {
        isActive.value = !isActive.value;
      }
    };

    return {
      isActive,
      isDisabled,
      tolerance,
      toggleActive,
    };
  },
});
</script>

<style scoped>
.fill-tool {
  display: flex;
  flex-direction: column;
  align-items: center;
}

button {
  cursor: pointer;
  padding: 8px 16px;
  border: none;
  background-color: var(--button-bg);
  color: var(--button-text-color);
  transition: background-color 0.3s;
}

button:disabled {
  background-color: var(--button-disabled-bg);
  cursor: not-allowed;
}

button.active {
  background-color: var(--button-active-bg);
}

.fill-options {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

label {
  margin-bottom: 5px;
  color: var(--label-text-color);
}

input[type="range"] {
  width: 100px;
}
</style>