<template>
  <div class="captcha-container">
    <div class="captcha" :class="{ 'captcha--error': hasError, 'captcha--solved': isSolved }">
      <span v-if="!isSolved">{{ captchaText }}</span>
      <span v-else>✔ Solved</span>
    </div>
    <button @click="solveCaptcha" :disabled="isSolved" aria-label="solve captcha">Solve</button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'Captcha',
  props: {
    captchaText: {
      type: String,
      default: 'Please solve the captcha',
    },
  },
  setup(props) {
    const isSolved = ref(false);
    const hasError = ref(false);

    const solveCaptcha = () => {
      if (props.captchaText === 'Please solve the captcha') {
        isSolved.value = true;
        hasError.value = false;
      } else {
        hasError.value = true;
      }
    };

    return {
      isSolved,
      hasError,
      solveCaptcha,
    };
  },
});
</script>

<style scoped lang="css">
@import './Captcha.css';
</style>