<script lang="ts">
  export let password: string = '';
  export let confirmPassword: string = '';
  export let disabled: boolean = false;

  let passwordsMatch: boolean = true;

  $: passwordsMatch = password === confirmPassword;
</script>

<div class="password-confirmation-field" aria-label="Password Confirmation Field">
  <input
    type="password"
    bind:value={password}
    placeholder="Enter password"
    disabled={disabled}
    aria-disabled={disabled}
    aria-label="Password"
  />
  <input
    type="password"
    bind:value={confirmPassword}
    placeholder="Confirm password"
    disabled={disabled}
    aria-disabled={disabled}
    aria-label="Confirm Password"
  />
  {#if !passwordsMatch}
    <p class="error" aria-live="assertive">Passwords do not match</p>
  {/if}
</div>

<style lang="css">
  @import './PasswordConfirmationField.css';
</style>