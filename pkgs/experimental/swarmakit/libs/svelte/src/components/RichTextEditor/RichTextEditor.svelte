<script lang="ts">
  import { onMount } from 'svelte';
  import Quill from 'quill';

  export let content: string = '';
  export let readOnly: boolean = false;

  let editorContainer: HTMLDivElement;

  onMount(() => {
    const quill = new Quill(editorContainer, {
      theme: 'snow',
      modules: {
        toolbar: !readOnly
          ? [
              ['bold', 'italic', 'underline', 'strike'],
              ['blockquote', 'code-block'],
              [{ header: 1 }, { header: 2 }],
              [{ list: 'ordered' }, { list: 'bullet' }],
              [{ script: 'sub' }, { script: 'super' }],
              [{ indent: '-1' }, { indent: '+1' }],
              [{ direction: 'rtl' }],
              [{ size: ['small', false, 'large', 'huge'] }],
              [{ header: [1, 2, 3, 4, 5, 6, false] }],
              [{ color: [] }, { background: [] }],
              [{ font: [] }],
              [{ align: [] }],
              ['clean']
            ]
          : false
      },
      readOnly
    });

    quill.setContents(quill.clipboard.convert({html:content}));

    quill.on('text-change', () => {
      content = quill.root.innerHTML;
    });
  });
</script>

<div class="rich-text-editor" bind:this={editorContainer}></div>

<style lang="css">
  @import './RichTextEditor.css';
</style>