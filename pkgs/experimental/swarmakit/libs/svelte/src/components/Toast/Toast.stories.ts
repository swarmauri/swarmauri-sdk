import Toast from './Toast.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<Toast> = {
  title: 'component/Indicators/Toast',
  component: Toast,
  tags: ['autodocs'],
  argTypes: {
    message: { control: 'text' },
    type: { control: 'select', options: ['success', 'error', 'warning', 'info'] },
    visible: { control: 'boolean' }
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

const Template:StoryFn<Toast> = (args) => ({
  Component: Toast,
  props:args,
}) 

export const Default = Template.bind ({});
Default.args = {
  message: 'This is a default toast message.',
  type: 'info',
  visible: true
}

export const Success = Template.bind ({});
Success.args = {
  message: 'Operation completed successfully!',
  type: 'success',
  visible: true
};


export const Error = Template.bind ({});
Error.args = {
  message: 'There was an error processing your request.',
  type: 'error',
  visible: true
};

export const Warning = Template.bind ({});
Warning.args = {
  message: 'This is a warning message.',
  type: 'warning',
  visible: true
};

export const Info = Template.bind ({});
Info.args = {
  message: 'This is some informative text.',
  type: 'info',
  visible: true
};

export const Dismissed = Template.bind ({});
Dismissed.args = {
  message: 'This message has been dismissed.',
  type: 'info',
  visible: false
};