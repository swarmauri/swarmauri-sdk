<script lang="ts">
  export let question: string;
  export let onSolve: (answer: string) => void;
  export let errorMessage: string = '';
  export let solved: boolean = false;

  let userAnswer: string = '';

  function handleSubmit() {
    onSolve(userAnswer);
  }
</script>

<div class="captcha-container">
  <p>{question}</p>
  <input
    type="text"
    bind:value={userAnswer}
    placeholder="Type your answer"
    aria-label="Captcha input"
    aria-invalid={errorMessage ? 'true' : 'false'}
  />
  <button on:click={handleSubmit} disabled={solved}>Submit</button>
  {#if errorMessage}
    <p class="error-message" role="alert">{errorMessage}</p>
  {/if}
  {#if solved}
    <p class="solved-message">Captcha Solved!</p>
  {/if}
</div>

<style lang="css">
  @import './Captcha.css';
</style>