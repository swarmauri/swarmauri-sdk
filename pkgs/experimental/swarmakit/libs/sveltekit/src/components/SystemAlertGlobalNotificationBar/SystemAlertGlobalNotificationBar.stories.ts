import SystemAlertGlobalNotificationBar from './SystemAlertGlobalNotificationBar.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<SystemAlertGlobalNotificationBar> = {
  title: 'component/Indicators/SystemAlertGlobalNotificationBar',
  component: SystemAlertGlobalNotificationBar,
  tags: ['autodocs'],
  argTypes: {
    message: { control: 'text' },
    type: { 
      control: { type: 'select' },
      options: ['success', 'error', 'warning', 'info']
    },
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

const Template:StoryFn<SystemAlertGlobalNotificationBar> = (args) => ({
  Component: SystemAlertGlobalNotificationBar,
  props:args,
});

export const Default = Template.bind({});
Default.args = {
  message: 'This is an information alert!',
  type: 'info'
};

export const Success = Template.bind({});
Success.args = {
  message: 'Operation completed successfully!',
  type: 'success'
};

export const Error = Template.bind({});
Error.args = {
  message: 'An error has occured!',
  type: 'error'
};

export const Warning = Template.bind({});
Warning.args = {
  message: 'Please be aware of the following warning!',
  type: 'warning'
};

export const Info = Template.bind({});
Info.args = {
message: 'This is an information alert!',
  type: 'info'
};