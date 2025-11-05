import { Meta, StoryFn } from '@storybook/vue3';
import ImageChoicePoll from './ImageChoicePoll.vue';

export default {
  title: 'component/Polls/ImageChoicePoll',
  component: ImageChoicePoll,
  tags: ['autodocs'],
  argTypes: {
    question: { control: 'text' },
    options: { control: 'object' },
    initialValue: { control: 'number' },
    resultsVisible: { control: 'boolean' },
    disabled: { control: 'boolean' },
  }
} as Meta<typeof ImageChoicePoll>;

const Template: StoryFn<typeof ImageChoicePoll> = (args) => ({
  components: { ImageChoicePoll },
  setup() {
    return { args };
  },
  template: '<ImageChoicePoll v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  question: 'Which image do you prefer?',
  options: [
    { image: 'link-to-image-1.jpg', alt: 'Image 1' },
    { image: 'link-to-image-2.jpg', alt: 'Image 2' },
    { image: 'link-to-image-3.jpg', alt: 'Image 3' }
  ],
  initialValue: undefined,
  resultsVisible: false,
  disabled: false
};

export const Unanswered = Template.bind({});
Unanswered.args = { ...Default.args };

export const Answered = Template.bind({});
Answered.args = {
  ...Default.args,
  initialValue: 1
};

export const ResultsVisible = Template.bind({});
ResultsVisible.args = {
  ...Default.args,
  resultsVisible: true,
  initialValue: 2
};

export const Disabled = Template.bind({});
Disabled.args = {
  ...Default.args,
  disabled: true
};