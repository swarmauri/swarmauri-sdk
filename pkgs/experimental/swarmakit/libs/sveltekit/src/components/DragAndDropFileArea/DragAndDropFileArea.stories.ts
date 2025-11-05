import DragAndDropFileArea from './DragAndDropFileArea.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<DragAndDropFileArea> = {
  title: 'component/Forms/DragAndDropFileArea',
  component: DragAndDropFileArea,
  tags: ['autodocs'],
  argTypes: {
    disabled: { control: 'boolean' },
    multiple: { control: 'boolean' },
    acceptedTypes: { control: 'text' },
    errorMessage: { control: 'text' },
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

const Template:StoryFn<DragAndDropFileArea> = (args) => ({
  Component: DragAndDropFileArea,
  props: args,
});

export const Default = Template.bind({});
Default.args = {
  disabled: false,
  multiple: true,
  acceptedTypes:'',
  errorMessage:'',
};

export const Dragging = Template.bind({});
Dragging.args = {
  disabled: false,
  multiple: true,
  acceptedTypes:'',
  errorMessage:'',
};

export const FileHover = Template.bind({});
FileHover.args = {
  disabled: false,
  multiple: true,
  acceptedTypes:'',
  errorMessage:'',
};

export const FileDropped = Template.bind({});
FileDropped.args = {
  disabled: false,
  multiple: true,
  acceptedTypes:'',
  errorMessage:'',
};

export const FileUploading = Template.bind({});
FileUploading.args = {
  disabled: true,
  multiple: true,
  acceptedTypes:'',
  errorMessage:'',
};

export const Error = Template.bind({});
Error.args = {
  disabled: false,
  multiple: true,
  acceptedTypes:'',
  errorMessage:'Invalid file type.',
};

export const Disabled = Template.bind({});
Disabled.args = {
  disabled: true,
  multiple: true,
  acceptedTypes:'',
  errorMessage:'',
};