import { Meta, StoryFn } from '@storybook/vue3';
import MultipleChoicePoll from './MultipleChoicePoll.vue';

export default {
  title: 'component/Polls/MultipleChoicePoll',
  component: MultipleChoicePoll,
  tags: ['autodocs'],
  argTypes: {
    question: { control: 'text' },
    options: { control: 'object' },
    isDisabled: { control: 'boolean' },
    showResults: { control: 'boolean' },
  },
} as Meta;

const Template: StoryFn = (args) => ({
  components: { MultipleChoicePoll },
  setup() {
    return { args };
  },
  template: '<MultipleChoicePoll v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  question: 'Select your favorite fruits:',
  options: ['Apple', 'Banana', 'Cherry'],
  isDisabled: false,
  showResults: false,
};

export const Unanswered = Template.bind({});
Unanswered.args = {
  ...Default.args,
  showResults: false,
};

export const PartiallyAnswered = Template.bind({});
PartiallyAnswered.args = {
  ...Default.args,
  selectedOptions: ['Apple'],
  showResults: false,
};

export const FullyAnswered = Template.bind({});
FullyAnswered.args = {
  ...Default.args,
  selectedOptions: ['Apple', 'Banana', 'Cherry'],
  showResults: false,
};

export const ResultsVisible = Template.bind({});
ResultsVisible.args = {
  ...Default.args,
  showResults: true,
};

export const Disabled = Template.bind({});
Disabled.args = {
  ...Default.args,
  isDisabled: true,
};