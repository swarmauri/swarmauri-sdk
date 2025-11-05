<script lang="ts">
  export let status: 'uploading' | 'downloading' | 'completed' | 'paused' | 'failed' = 'uploading';
  export let fileName: string = '';
  export let progress: number = 0;

  const statuses = {
    uploading: 'Uploading...',
    downloading: 'Downloading...',
    completed: 'Completed',
    paused: 'Paused',
    failed: 'Failed'
  };
</script>

<div class="upload" role="status" aria-live="polite">
  <p>{fileName}</p>
  <p>{statuses[status]}</p>
  {#if status === 'uploading' || status === 'downloading'}
    <progress max="100" value={progress} aria-valuenow={progress} aria-valuemin="0" aria-valuemax="100"></progress>
  {/if}
</div>

<style lang="css">
  @import './Upload.css';
</style>