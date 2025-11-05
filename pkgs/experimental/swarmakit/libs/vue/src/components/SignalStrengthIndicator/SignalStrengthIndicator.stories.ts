import { Meta, StoryFn } from '@storybook/vue3';
import SignalStrengthIndicator from './SignalStrengthIndicator.vue';

export default {
  title: 'component/Indicators/SignalStrengthIndicator',
  component: SignalStrengthIndicator,
  tags: ['autodocs'],
  argTypes: {
    strength: { control: 'number' },
  },
} as Meta<typeof SignalStrengthIndicator>;

const Template: StoryFn<typeof SignalStrengthIndicator> = (args) => ({
  components: { SignalStrengthIndicator },
  setup() {
    return { args };
  },
  template: `<SignalStrengthIndicator v-bind="args" />`,
});

export const Default = Template.bind({});
Default.args = {
  strength: 3,
};

export const FullSignal = Template.bind({});
FullSignal.args = {
  strength: 5,
};

export const WeakSignal = Template.bind({});
WeakSignal.args = {
  strength: 1,
};

export const NoSignal = Template.bind({});
NoSignal.args = {
  strength: 0,
};