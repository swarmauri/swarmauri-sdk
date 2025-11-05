import { Meta, StoryFn } from '@storybook/vue3';
import Badge from './Badge.vue';

export default {
  title: 'component/Indicators/Badge',
  component: Badge,
  tags: ['autodocs'],
  argTypes: {
    type: {
      control: { type: 'select', options: ['default', 'notification', 'status-indicator'] },
    },
  },
} as Meta<typeof Badge>;

const Template: StoryFn<typeof Badge> = (args) => ({
  components: { Badge },
  setup() {
    return { args };
  },
  template: `<Badge v-bind="args">{{ args.type }}</Badge>`,
});

export const Default = Template.bind({});
Default.args = {
  type: 'default',
};

export const Notification = Template.bind({});
Notification.args = {
  type: 'notification',
};

export const StatusIndicator = Template.bind({});
StatusIndicator.args = {
  type: 'status-indicator',
};