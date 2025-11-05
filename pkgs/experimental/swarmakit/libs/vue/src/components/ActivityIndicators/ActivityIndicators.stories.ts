import { Meta, StoryFn } from '@storybook/vue3';
import ActivityIndicators from './ActivityIndicators.vue';

// Define the metadata for the story
export default {
  component: ActivityIndicators,
  title: 'component/Indicators/ActivityIndicators',
  tags: ['autodocs'],
  argTypes: {
    type: {
      control: { type: 'select' },
      options: ['loading', 'success', 'error'],
    },
    message: {
      control: 'text',
    },
  },
} as Meta<typeof ActivityIndicators>;

// Define the template with explicit type for args
const Template: StoryFn<typeof ActivityIndicators> = (args) => ({
  components: { ActivityIndicators },
  setup() {
    return { args };
  },
  template: '<ActivityIndicators v-bind="args" />', // Use v-bind to bind all props
});

export const Default = Template.bind({});
Default.args = {
  type: 'loading',
  message: 'Loading...',
};

export const Loading = Template.bind({});
Loading.args = {
  type: 'loading',
  message: 'Loading...',
};

export const Success = Template.bind({});
Success.args = {
  type: 'success',
  message: 'Operation successful!',
};

export const Error = Template.bind({});
Error.args = {
  type: 'error',
  message: 'An error occurred!',
};
