<template>
  <div class="password-confirmation-container">
    <input 
      type="password" 
      v-model="password" 
      :disabled="disabled" 
      placeholder="Enter password" 
      aria-label="Enter password"
    />
    <input 
      type="password" 
      v-model="confirmPassword" 
      :disabled="disabled" 
      placeholder="Confirm password" 
      aria-label="Confirm password"
    />
    <p :class="{'match': isMatching, 'not-match': !isMatching}">
      {{ isMatching ? 'Passwords match' : 'Passwords do not match' }}
    </p>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';

export default defineComponent({
  name: 'PasswordConfirmationField',
  props: {
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  setup() {
    const password = ref('');
    const confirmPassword = ref('');
    
    const isMatching = computed(() => password.value === confirmPassword.value);

    return { password, confirmPassword, isMatching };
  },
});
</script>

<style scoped lang="css">
@import './PasswordConfirmationField.css';
</style>