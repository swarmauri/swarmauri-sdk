import { Meta, StoryFn } from '@storybook/vue3';
import SingleChoicePoll from './SingleChoicePoll.vue';

export default {
  title: 'component/Polls/SingleChoicePoll',
  component: SingleChoicePoll,
  tags: ['autodocs'],
  argTypes: {
    question: { control: 'text' },
    options: { control: 'object' },
    isDisabled: { control: 'boolean' },
    showResults: { control: 'boolean' },
  },
} as Meta;

const Template: StoryFn = (args) => ({
  components: { SingleChoicePoll },
  setup() {
    return { args };
  },
  template: '<SingleChoicePoll v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  question: 'What is your favorite color?',
  options: ['Red', 'Green', 'Blue'],
  isDisabled: false,
  showResults: false,
};

export const Unanswered = Template.bind({});
Unanswered.args = {
  ...Default.args,
  showResults: false,
};

export const Answered = Template.bind({});
Answered.args = {
  ...Default.args,
  showResults: true,
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