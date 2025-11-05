import { Meta, StoryFn } from '@storybook/vue3';
import PokerTimer from './PokerTimer.vue';

export default {
  title: 'component/Poker/PokerTimer',
  component: PokerTimer,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
  argTypes: {
    initialTime: { control: 'number' },
  },
} as Meta<typeof PokerTimer>;

const Template: StoryFn<typeof PokerTimer> = (args) => ({
  components: { PokerTimer },
  setup() {
    return { args };
  },
  template: '<PokerTimer v-bind="args" />',
});

export const Active = Template.bind({});
Active.args = {
  initialTime: 30,
};

export const Paused = Template.bind({});
Paused.args = {
  initialTime: 30,
};

export const Expired = Template.bind({});
Expired.args = {
  initialTime: 0,
};