import { Meta, StoryFn } from '@storybook/vue3';
import InteractivePollResults from './InteractivePollResults.vue';

export default {
  title: 'component/Indicators/InteractivePollResults',
  component: InteractivePollResults,
  tags: ['autodocs'],
  argTypes: {
    title: { control: 'text' },
    options: { control: 'object' },
    state: { control: { type: 'select', options: ['live', 'completed', 'closed'] } },
  },
} as Meta<typeof InteractivePollResults>;

const Template: StoryFn<typeof InteractivePollResults> = (args) => ({
  components: { InteractivePollResults },
  setup() {
    return { args };
  },
  template: `<InteractivePollResults v-bind="args" />`,
});

export const Default = Template.bind({});
Default.args = {
  title: 'Poll Results',
  options: [
    { id: 1, text: 'Option A', percentage: 40 },
    { id: 2, text: 'Option B', percentage: 30 },
    { id: 3, text: 'Option C', percentage: 30 },
  ],
  state: 'live',
};

export const LiveResults = Template.bind({});
LiveResults.args = {
  ...Default.args,
  state: 'live',
};

export const Completed = Template.bind({});
Completed.args = {
  ...Default.args,
  state: 'completed',
};

export const Closed = Template.bind({});
Closed.args = {
  ...Default.args,
  state: 'closed',
};