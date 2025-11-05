import { Meta, StoryFn } from '@storybook/vue3';
import Notification from './Notification.vue';

export default {
  title: 'component/Miscellaneous/Notification',
  component: Notification,
  tags: ['autodocs'],
} as Meta<typeof Notification>;

const Template: StoryFn<typeof Notification> = (args) => ({
  components: { Notification },
  setup() {
    return { args };
  },
  template: '<Notification v-bind="args" />',
});

export const Success = Template.bind({});
Success.args = { notificationType: 'success', message: 'Operation was successful.' };

export const Error = Template.bind({});
Error.args = { notificationType: 'error', message: 'An error has occurred.' };

export const Warning = Template.bind({});
Warning.args = { notificationType: 'warning', message: 'Warning: Check your input.' };

export const Dismissed = Template.bind({});
Dismissed.args = { notificationType: 'success', message: 'This notification has been dismissed.', isDismissed: true };