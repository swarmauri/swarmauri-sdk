import FileUpload from './FileUpload.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<FileUpload> = {
  title: 'component/Forms/FileUpload',
  component: FileUpload,
  tags: ['autodocs'],
  argTypes: {
    multiple: { control: 'boolean' },
    uploadProgress: { control: 'number', min: 0, max: 100 },
    isDragAndDrop: { control: 'boolean' },
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

const Template:StoryFn<FileUpload> = (args) => ({
  Component:FileUpload,
  props:args,
});

export const Default = Template.bind({});
Default.args = {
  multiple: false,
  uploadProgress: 0,
  isDragAndDrop: false,
};

export const SingleFile = Template.bind({});
SingleFile.args = {
  multiple: false,
  uploadProgress: 0,
  isDragAndDrop: false,
};

export const MultipleFiles = Template.bind({});
MultipleFiles.args = {
  multiple: true,
  uploadProgress: 0,
  isDragAndDrop: false,
};

export const DragAndDrop = Template.bind({});
DragAndDrop.args = {
  multiple: false,
  uploadProgress: 0,
  isDragAndDrop: true,
};

export const Progress = Template.bind({});
Progress.args = {
  multiple: false,
  uploadProgress: 50,
  isDragAndDrop: false,
};

// type Story = StoryObj<typeof meta>;

// export const Default: Story = {
//   args: {
//     multiple: false,
//     uploadProgress: 0,
//     isDragAndDrop: false,
//   }
// };

// export const SingleFile: Story = {
//   args: {
//     multiple: false,
//     uploadProgress: 0,
//     isDragAndDrop: false,
//   }
// };

// export const MultipleFiles: Story = {
//   args: {
//     multiple: true,
//     uploadProgress: 0,
//     isDragAndDrop: false,
//   }
// };

// export const DragAndDrop: Story = {
//   args: {
//     multiple: false,
//     uploadProgress: 0,
//     isDragAndDrop: true,
//   }
// };

// export const Progress: Story = {
//   args: {
//     multiple: false,
//     uploadProgress: 50,
//     isDragAndDrop: false,
//   }
// };