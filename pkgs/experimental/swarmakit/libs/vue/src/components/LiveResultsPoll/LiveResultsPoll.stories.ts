import { Meta, StoryFn } from '@storybook/vue3';
import LiveResultsPoll from './LiveResultsPoll.vue';

export default {
  title: 'component/Polls/LiveResultsPoll',
  component: LiveResultsPoll,
  tags: ['autodocs'],
  argTypes: {
    question: { control: 'text' },
    options: { control: 'object' },
    initialValue: { control: 'number' },
    liveResultsVisible: { control: 'boolean' },
    closed: { control: 'boolean' },
  }
} as Meta<typeof LiveResultsPoll>;

const Template: StoryFn<typeof LiveResultsPoll> = (args) => ({
  components: { LiveResultsPoll },
  setup() {
    return { args };
  },
  template: '<LiveResultsPoll v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  question: 'Which option do you prefer?',
  options: [
    { text: 'Option 1', votes: 10 },
    { text: 'Option 2', votes: 20 },
    { text: 'Option 3', votes: 30 }
  ],
  initialValue: undefined,
  liveResultsVisible: false,
  closed: false
};

export const Unanswered = Template.bind({});
Unanswered.args = { ...Default.args };

export const Answered = Template.bind({});
Answered.args = {
  ...Default.args,
  initialValue: 1
};

export const LiveResultsVisible = Template.bind({});
LiveResultsVisible.args = {
  ...Default.args,
  liveResultsVisible: true
};

export const Closed = Template.bind({});
Closed.args = {
  ...Default.args,
  closed: true
};