import Upload from './Upload.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<Upload> = {
  title: 'component/Indicators/Upload',
  component: Upload,
  tags: ['autodocs'],
  argTypes: {
    status: { control: 'select', options: ['uploading', 'downloading', 'completed', 'paused', 'failed'] },
    fileName: { control: 'text' },
    progress: { control: 'number' }
  },
  parameters: {
    layout: 'centered',
    viewport: {
      viewports: {
        smallMobile: { name: 'Small Mobile', styles: { width: '320px', height: '568px' } },
        largeMobile: { name: 'Large Mobile', styles: { width: '414px', height: '896px' } },
        tablet: { name: 'Tablet', styles: { width: '768px', height: '1024px' } },
        desktop: { name: 'Desktop', styles: { width: '1024px', height: '768px' } },
      }
    }
  }
};

export default meta;

const Template:StoryFn<Upload> = (args) => ({
  Component: Upload,
  props:args,
}); 

export const Default = Template.bind({});
Default.args = {
  fileName: 'example.txt',
  status: 'uploading',
  progress: 50
};

export const Uploading = Template.bind({});
Uploading.args = {
  fileName: 'example.txt',
  status: 'uploading',
  progress: 50
};

export const Downloading = Template.bind({});
Downloading.args = {
  fileName: 'downloading_file.txt',
  status: 'downloading',
  progress: 60
};

export const Completed = Template.bind({});
Completed.args = {
  fileName: 'completed_file.txt',
  status: 'completed',
  progress: 100
};

export const Paused = Template.bind({});
Paused.args = {
  fileName: 'paused_file.txt',
  status: 'paused',
  progress: 70
};

export const Failed = Template.bind({});
Failed.args = {
  fileName: 'paused_file.txt',
  status: 'paused',
  progress: 70
};