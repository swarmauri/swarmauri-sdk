import { Meta, StoryFn } from '@storybook/vue3';
import StatusDots from './StatusDots.vue';

export default {
  title: 'component/Indicators/StatusDots',
  component: StatusDots,
  tags: ['autodocs'],
  argTypes: {
    status: {
      control: 'select',
      options: ['online', 'offline', 'busy', 'idle'],
    },
  },
} as Meta<typeof StatusDots>;

const Template: StoryFn<typeof StatusDots> = (args) => ({
  components: { StatusDots },
  setup() {
    return { args };
  },
  template: `<StatusDots v-bind="args" />`,
});

export const Default = Template.bind({});
Default.args = {
  status: 'offline',
};

export const Online = Template.bind({});
Online.args = {
  status: 'online',
};

export const Offline = Template.bind({});
Offline.args = {
  status: 'offline',
};

export const Busy = Template.bind({});
Busy.args = {
  status: 'busy',
};

export const Idle = Template.bind({});
Idle.args = {
  status: 'idle',
};