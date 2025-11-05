import { Meta, StoryFn } from '@storybook/vue3';
import SystemAlertGlobalNotificationBar from './SystemAlertGlobalNotificationBar.vue';

export default {
  title: 'component/Indicators/SystemAlertGlobalNotificationBar',
  component: SystemAlertGlobalNotificationBar,
  tags: ['autodocs'],
  argTypes: {
    type: {
      control: { type: 'select', options: ['success', 'error', 'warning', 'info'] },
    },
    message: {
      control: 'text',
    },
  },
} as Meta<typeof SystemAlertGlobalNotificationBar>;

const Template: StoryFn<typeof SystemAlertGlobalNotificationBar> = (args) => ({
  components: { SystemAlertGlobalNotificationBar },
  setup() {
    return { args };
  },
  template: `<SystemAlertGlobalNotificationBar v-bind="args" />`,
});

export const Default = Template.bind({});
Default.args = {
  type: 'info',
  message: 'This is an informational message.',
};

export const Success = Template.bind({});
Success.args = {
  type: 'success',
  message: 'Operation completed successfully!',
};

export const Error = Template.bind({});
Error.args = {
  type: 'error',
  message: 'There was an error processing your request.',
};

export const Warning = Template.bind({});
Warning.args = {
  type: 'warning',
  message: 'Please be aware of the potential issues.',
};

export const Info = Template.bind({});
Info.args = {
  type: 'info',
  message: 'This is an informational message.',
};