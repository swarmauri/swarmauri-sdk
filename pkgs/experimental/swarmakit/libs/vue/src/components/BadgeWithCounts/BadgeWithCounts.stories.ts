import { Meta, StoryFn } from '@storybook/vue3';
import BadgeWithCounts from './BadgeWithCounts.vue';

export default {
  title: 'component/Indicators/BadgeWithCounts',
  component: BadgeWithCounts,
  tags: ['autodocs'],
  argTypes: {
    count: {
      control: { type: 'number' },
    },
  },
} as Meta<typeof BadgeWithCounts>;

const Template: StoryFn<typeof BadgeWithCounts> = (args) => ({
  components: { BadgeWithCounts },
  setup() {
    return { args };
  },
  template: `<BadgeWithCounts v-bind="args" />`,
});

export const Default = Template.bind({});
Default.args = {
  count: 0,
};

export const Zero = Template.bind({});
Zero.args = {
  count: 0,
};

export const Active = Template.bind({});
Active.args = {
  count: 5,
};

export const Overflow = Template.bind({});
Overflow.args = {
  count: 100,
};