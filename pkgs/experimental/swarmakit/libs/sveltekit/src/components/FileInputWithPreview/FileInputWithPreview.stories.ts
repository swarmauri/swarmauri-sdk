import FileInputWithPreview from './FileInputWithPreview.svelte';

export default {
  title: 'Forms/FileInputWithPreview',
  component: FileInputWithPreview,
  tags: ['autodocs'],
};

export const FileUploaded = {
  args: {
    error: '',
    disabled: false,
  },
};

export const PreviewDisplayed = {
  args: {
    error: '',
    disabled: false,
  },
};

export const Error = {
  args: {
    error: 'File format not supported',
    disabled: false,
  },
};

export const Disabled = {
  args: {
    error: '',
    disabled: true,
  },
};