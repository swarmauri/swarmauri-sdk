<template>
  <div class="text-tool">
    <button @click="toggleActive" :class="{ active: isActive }" aria-label="Text Tool">Text Tool</button>
    <div v-if="isActive" class="text-options">
      <label for="font-style">Font Style:</label>
      <select id="font-style" v-model="fontStyle">
        <option v-for="style in fontStyles" :key="style" :value="style">{{ style }}</option>
      </select>
      
      <label for="font-size">Font Size:</label>
      <input id="font-size" type="number" v-model="fontSize" />

      <label for="font-color">Color:</label>
      <input id="font-color" type="color" v-model="fontColor" />

      <label for="alignment">Alignment:</label>
      <select id="alignment" v-model="alignment">
        <option v-for="align in alignments" :key="align" :value="align">{{ align }}</option>
      </select>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'TextTool',
  setup() {
    const isActive = ref(false);
    const fontStyle = ref('Arial');
    const fontSize = ref(16);
    const fontColor = ref('#000000');
    const alignment = ref('left');
    
    const fontStyles = ['Arial', 'Verdana', 'Times New Roman'];
    const alignments = ['left', 'center', 'right'];

    const toggleActive = () => {
      isActive.value = !isActive.value;
    };

    return {
      isActive,
      fontStyle,
      fontSize,
      fontColor,
      alignment,
      fontStyles,
      alignments,
      toggleActive,
    };
  },
});
</script>

<style scoped>
.text-tool {
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

button.active {
  background-color: var(--button-active-bg);
}

.text-options {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

label, select, input {
  margin-bottom: 5px;
  color: var(--label-text-color);
}

input[type="color"] {
  border: none;
  width: 50px;
  height: 30px;
}
</style>