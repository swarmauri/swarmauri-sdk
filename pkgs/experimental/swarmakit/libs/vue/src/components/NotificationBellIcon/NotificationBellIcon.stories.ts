import { Meta, StoryFn } from '@storybook/vue3';
import NotificationBellIcon from './NotificationBellIcon.vue';

export default {
  title: 'component/Indicators/NotificationBellIcon',
  component: NotificationBellIcon,
  tags: ['autodocs'],
  argTypes: {
    hasNotifications: { control: 'boolean' },
    dismissed: { control: 'boolean' },
  },
} as Meta<typeof NotificationBellIcon>;

const Template: StoryFn<typeof NotificationBellIcon> = (args) => ({
  components: { NotificationBellIcon },
  setup() {
    return { args };
  },
  template: `<NotificationBellIcon v-bind="args" />`,
});

export const Default = Template.bind({});
Default.args = {
  hasNotifications: false,
  dismissed: false,
};

export const NoNotifications = Template.bind({});
NoNotifications.args = {
  hasNotifications: false,
  dismissed: false,
};

export const NewNotifications = Template.bind({});
NewNotifications.args = {
  hasNotifications: true,
  dismissed: false,
};

export const Dismissed = Template.bind({});
Dismissed.args = {
  hasNotifications: false,
  dismissed: true,
};