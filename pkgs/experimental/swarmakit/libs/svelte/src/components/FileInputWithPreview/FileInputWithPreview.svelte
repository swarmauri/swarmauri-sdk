<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  let file: File | null = null;
  let previewUrl: string | null = null;
  export let error: string = "";
  export let disabled: boolean = false;

  const dispatch = createEventDispatcher();

  function handleFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    const files = input.files;
    if (files && files[0]) {
      file = files[0];
      previewUrl = URL.createObjectURL(file);
      error = "";
      dispatch('filechange', file);
    } else {
      file = null;
      previewUrl = null;
    }
  }

  function clearPreview() {
    file = null;
    previewUrl = null;
    error = "";
  }
</script>

<div class="file-input-with-preview">
  <input 
    type="file" 
    on:change={handleFileChange} 
    accept="image/*" 
    aria-label="Upload File" 
    {disabled}
  />
  {#if previewUrl}
    <div class="preview">
      <img src={previewUrl} alt="File preview" />
      <button on:click={clearPreview} aria-label="Clear Preview" disabled={disabled}>Clear</button>
    </div>
  {/if}
  {#if error}
    <div class="error" aria-live="assertive">{error}</div>
  {/if}
</div>

<style lang="css">
  .file-input-with-preview input[type="file"] {
    margin: 5px;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 14px;
  }

  .file-input-with-preview .preview {
    margin-top: 10px;
    display: flex;
    align-items: center;
  }

  .file-input-with-preview .preview img {
    max-width: 100px;
    margin-right: 10px;
  }

  .file-input-with-preview .preview button {
    padding: 5px 10px;
    background-color: #007bff;
    color: #fff;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .file-input-with-preview .preview button:disabled {
    background-color: #e9ecef;
    cursor: not-allowed;
  }

  .file-input-with-preview .error {
    color: red;
    margin-top: 5px;
  }
</style>