import { Meta, StoryFn } from '@storybook/vue3';
import ThumbsUpThumbsDownPoll from './ThumbsUpThumbsDownPoll.vue';

export default {
  title: 'component/Polls/ThumbsUpThumbsDownPoll',
  component: ThumbsUpThumbsDownPoll,
  tags: ['autodocs'],
  argTypes: {
    question: { control: 'text' },
    initialSelection: { control: 'text' },
    isDisabled: { control: 'boolean' },
    showResults: { control: 'boolean' },
  },
} as Meta;

const Template: StoryFn = (args) => ({
  components: { ThumbsUpThumbsDownPoll },
  setup() {
    return { args };
  },
  template: '<ThumbsUpThumbsDownPoll v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  question: 'Do you agree with this statement?',
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
  initialSelection: 'up',
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