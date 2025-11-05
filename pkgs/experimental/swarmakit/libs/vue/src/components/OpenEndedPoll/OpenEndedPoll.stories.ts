import { Meta, StoryFn } from '@storybook/vue3';
import OpenEndedPoll from './OpenEndedPoll.vue';

export default {
  title: 'component/Polls/OpenEndedPoll',
  component: OpenEndedPoll,
  tags: ['autodocs'],
  argTypes: {
    question: { control: 'text' },
    initialResponses: { control: 'object' },
    resultsVisible: { control: 'boolean' },
    disabled: { control: 'boolean' },
  }
} as Meta<typeof OpenEndedPoll>;

const Template: StoryFn<typeof OpenEndedPoll> = (args) => ({
  components: { OpenEndedPoll },
  setup() {
    return { args };
  },
  template: '<OpenEndedPoll v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  question: 'What are your thoughts on this topic?',
  initialResponses: [],
  resultsVisible: false,
  disabled: false,
};

export const Unanswered = Template.bind({});
Unanswered.args = { ...Default.args };

export const Answered = Template.bind({});
Answered.args = {
  ...Default.args,
  initialResponses: ['This is a great topic!', 'I have mixed feelings about this.']
};

export const ResultsVisible = Template.bind({});
ResultsVisible.args = {
  ...Default.args,
  resultsVisible: true,
  initialResponses: ['This is a great topic!', 'I have mixed feelings about this.']
};

export const Disabled = Template.bind({});
Disabled.args = {
  ...Default.args,
  disabled: true
};