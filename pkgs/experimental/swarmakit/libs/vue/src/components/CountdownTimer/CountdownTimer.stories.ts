import { Meta, StoryFn } from '@storybook/vue3';
import CountdownTimer from './CountdownTimer.vue';

export default {
  title: 'component/Indicators/CountdownTimer',
  component: CountdownTimer,
  tags: ['autodocs'],
  argTypes: {
    duration: {
      control: { type: 'number', min: 0 },
    },
  },
} as Meta<typeof CountdownTimer>;

const Template: StoryFn<typeof CountdownTimer> = (args) => ({
  components: { CountdownTimer },
  setup() {
    return { args };
  },
  template: `<CountdownTimer v-bind="args" />`,
});

export const Default = Template.bind({});
Default.args = {
  duration: 90, // 1 minute 30 seconds
};

export const Running = Template.bind({});
Running.args = {
  duration: 120,
};

export const Paused = Template.bind({});
Paused.args = {
  duration: 90,
  // To simulate paused state, manually set isPaused to true in the component
};

export const Completed = Template.bind({});
Completed.args = {
  duration: 0,
};