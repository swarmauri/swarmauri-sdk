<template>
  <div class="editor-container">
    <div 
      ref="editor" 
      :aria-label="`Rich text editor`" 
      :aria-readonly="readonly"
    ></div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import Quill from 'quill';
import 'quill/dist/quill.snow.css';

export default defineComponent({
  name: 'RichTextEditor',
  props: {
    readonly: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const editor = ref<HTMLDivElement | null>(null);

    onMounted(() => {
      if (editor.value) {
        new Quill(editor.value, {
          theme: 'snow',
          readOnly: props.readonly,
          modules: {
            toolbar: !props.readonly,
          },
        });
      }
    });

    return {
      editor,
    };
  },
});
</script>

<style scoped>
@import './RichTextEditor.css';
</style>