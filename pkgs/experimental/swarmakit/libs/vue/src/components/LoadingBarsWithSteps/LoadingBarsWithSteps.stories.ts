import { Meta, StoryFn } from '@storybook/vue3';
import LoadingBarsWithSteps from './LoadingBarsWithSteps.vue';

export default {
  title: 'component/Indicators/LoadingBarsWithSteps',
  component: LoadingBarsWithSteps,
  tags: ['autodocs'],
  argTypes: {
    steps: { control: 'object' },
    currentStep: { control: 'number' },
  },
} as Meta<typeof LoadingBarsWithSteps>;

const Template: StoryFn<typeof LoadingBarsWithSteps> = (args) => ({
  components: { LoadingBarsWithSteps },
  setup() {
    return { args };
  },
  template: `<LoadingBarsWithSteps v-bind="args" />`,
});

export const Default = Template.bind({});
Default.args = {
  steps: [
    { id: 1, label: 'Step 1' },
    { id: 2, label: 'Step 2' },
    { id: 3, label: 'Step 3' },
  ],
  currentStep: 1,
};

export const StepActive = Template.bind({});
StepActive.args = {
  ...Default.args,
  currentStep: 1,
};

export const StepCompleted = Template.bind({});
StepCompleted.args = {
  ...Default.args,
  currentStep: 3,
};

export const StepInactive = Template.bind({});
StepInactive.args = {
  ...Default.args,
  currentStep: 0,
};