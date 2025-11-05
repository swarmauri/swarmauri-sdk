import { Meta, StoryFn } from '@storybook/vue3';
import YesNoPoll from './YesNoPoll.vue';

export default {
  title: 'component/Polls/YesNoPoll',
  component: YesNoPoll,
  tags: ['autodocs'],
  argTypes: {
    question: { control: 'text' },
    initialSelection: { control: 'text' },
    isDisabled: { control: 'boolean' },
    showResults: { control: 'boolean' },
  },
} as Meta;

const Template: StoryFn = (args) => ({
  components: { YesNoPoll },
  setup() {
    return { args };
  },
  template: '<YesNoPoll v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  question: 'Do you accept the terms and conditions?',
  initialSelection: null,
  isDisabled: false,
  showResults: false,
};

export const Unanswered = Template.bind({});
Unanswered.args = {
  ...Default.args,
  initialSelection: null,
};

export const Answered = Template.bind({});
Answered.args = {
  ...Default.args,
  initialSelection: 'yes',
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