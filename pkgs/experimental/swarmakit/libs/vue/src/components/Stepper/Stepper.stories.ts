import { Meta, StoryFn } from '@storybook/vue3';
import Stepper from './Stepper.vue';

export default {
  title: 'component/Indicators/Stepper',
  component: Stepper,
  tags: ['autodocs'],
  argTypes: {
    steps: {
      control: 'object',
    },
  },
} as Meta<typeof Stepper>;

const Template: StoryFn<typeof Stepper> = (args) => ({
  components: { Stepper },
  setup() {
    return { args };
  },
  template: `<Stepper v-bind="args" />`,
});

export const Default = Template.bind({});
Default.args = {
  steps: [
    { label: 'Step 1', status: 'completed' },
    { label: 'Step 2', status: 'active' },
    { label: 'Step 3', status: 'disabled' },
  ],
};

export const Completed = Template.bind({});
Completed.args = {
  steps: [
    { label: 'Step 1', status: 'completed' },
    { label: 'Step 2', status: 'completed' },
    { label: 'Step 3', status: 'completed' },
  ],
};

export const Active = Template.bind({});
Active.args = {
  steps: [
    { label: 'Step 1', status: 'active' },
    { label: 'Step 2', status: 'active' },
    { label: 'Step 3', status: 'active' },
  ],
};

export const Disabled = Template.bind({});
Disabled.args = {
  steps: [
    { label: 'Step 1', status: 'disabled' },
    { label: 'Step 2', status: 'disabled' },
    { label: 'Step 3', status: 'disabled' },
  ],
};