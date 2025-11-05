<script lang="ts">
  export let multiple: boolean = false;
  export let uploadProgress: number = 0;
  export let isDragAndDrop: boolean = true;

  let files: File[] = [];

  function handleFileChange(event: Event) {
    const inputFiles = Array.from((event.target as HTMLInputElement).files || []);
    files = inputFiles;
  }

  function handleDragOver(event: DragEvent) {
    event.preventDefault();
  }

  function handleDrop(event: DragEvent) {
    event.preventDefault();
    const droppedFiles = Array.from(event.dataTransfer?.files || []);
    files = droppedFiles;
  }
</script>

<div
  class="file-upload"
  on:dragover={handleDragOver}
  on:drop={handleDrop}
  aria-label="File Upload"
  role='group'
>
  {#if isDragAndDrop}
    <div class="drop-area" tabindex="-1">
      Drag and drop files here or click to browse
    </div>
  {/if}
  <input
    type="file"
    class="file-input"
    multiple={multiple}
    on:change={handleFileChange}
    aria-hidden="true"
  />
  {#if uploadProgress > 0}
    <div class="progress-bar" role="progressbar" aria-valuenow={uploadProgress} aria-valuemin="0" aria-valuemax="100">
      <div class="progress" style="width: {uploadProgress}%"></div>
    </div>
  {/if}
</div>

<style lang="css">
  @import './FileUpload.css';
</style>