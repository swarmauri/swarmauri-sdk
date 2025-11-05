import { Meta, StoryFn } from '@storybook/vue3';
import BetSlider from './BetSlider.vue';

export default {
  title: 'component/Poker/BetSlider',
  component: BetSlider,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
  argTypes: {
    min: { control: 'number' },
    max: { control: 'number' },
    step: { control: 'number' },
    disabled: { control: 'boolean' },
  },
} as Meta<typeof BetSlider>;

const Template: StoryFn<typeof BetSlider> = (args) => ({
  components: { BetSlider },
  setup() {
    return { args };
  },
  template: '<BetSlider v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  min: 0,
  max: 100,
  step: 1,
  disabled: false,
};

export const Adjusted = Template.bind({});
Adjusted.args = {
  min: 0,
  max: 100,
  step: 1,
  disabled: false,
};

export const MaxBet = Template.bind({});
MaxBet.args = {
  min: 0,
  max: 100,
  step: 1,
  disabled: false,
};

export const Disabled = Template.bind({});
Disabled.args = {
  min: 0,
  max: 100,
  step: 1,
  disabled: true,
};