import { Meta, StoryFn } from '@storybook/vue3';
import Upload from './Upload.vue';

export default {
  title: 'component/Indicators/Upload',
  component: Upload,
  tags: ['autodocs'],
  argTypes: {
    message: {
      control: 'text',
    },
    status: {
      control: { type: 'select', options: ['uploading', 'downloading', 'completed', 'paused', 'failed'] },
    },
    progress: {
      control: { type: 'number', min: 0, max: 100 },
    },
  },
} as Meta<typeof Upload>;

const Template: StoryFn<typeof Upload> = (args) => ({
  components: { Upload },
  setup() {
    return { args };
  },
  template: `<Upload v-bind="args" />`,
});

export const Default = Template.bind({});
Default.args = {
  message: 'Uploading file...',
  status: 'uploading',
  progress: 50,
};

export const Uploading = Template.bind({});
Uploading.args = {
  message: 'Uploading file...',
  status: 'uploading',
  progress: 70,
};

export const Downloading = Template.bind({});
Downloading.args = {
  message: 'Downloading file...',
  status: 'downloading',
  progress: 30,
};

export const Completed = Template.bind({});
Completed.args = {
  message: 'Upload completed.',
  status: 'completed',
};

export const Paused = Template.bind({});
Paused.args = {
  message: 'Upload paused.',
  status: 'paused',
};

export const Failed = Template.bind({});
Failed.args = {
  message: 'Upload failed.',
  status: 'failed',
};