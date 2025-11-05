<script lang="ts">
  export let disabled: boolean = false;
  export let multiple: boolean = true;
  export let acceptedTypes: string = '';
  export let errorMessage: string = '';

  let dragging = false;
  let files: File[] = [];

  function handleDragOver(event: DragEvent) {
    event.preventDefault();
    if (!disabled) {
      dragging = true;
    }
  }

  function handleDragLeave() {
    dragging = false;
  }

  function handleDrop(event: DragEvent) {
    event.preventDefault();
    if (!disabled) {
      const droppedFiles = Array.from(event.dataTransfer?.files || []);
      files = validateFiles(droppedFiles);
      dragging = false;
    }
  }

  function validateFiles(droppedFiles: File[]): File[] {
    if (acceptedTypes) {
      const validFiles = droppedFiles.filter(file => acceptedTypes.includes(file.type));
      if (validFiles.length !== droppedFiles.length) {
        errorMessage = 'Some files have invalid types.';
      }
      return validFiles;
    }
    return droppedFiles;
  }

  function handleFileChange(event: Event) {
    const inputFiles = Array.from((event.target as HTMLInputElement).files || []);
    files = validateFiles(inputFiles);
  }
</script>

<div
  class="drop-area"
  class:dragging={dragging}
  on:dragover={handleDragOver}
  on:dragleave={handleDragLeave}
  on:drop={handleDrop}
  aria-disabled={disabled}
  role="group"
>
  <input
    type="file"
    class="file-input"
    multiple={multiple}
    accept={acceptedTypes}
    on:change={handleFileChange}
    aria-hidden="true"
    disabled={disabled}
  />
  <p>{dragging ? 'Drop files here...' : 'Drag and drop files here or click to browse'}</p>
  {#if errorMessage}
    <p class="error">{errorMessage}</p>
  {/if}
</div>

<style lang="css">
  @import './DragAndDropFileArea.css';
</style>