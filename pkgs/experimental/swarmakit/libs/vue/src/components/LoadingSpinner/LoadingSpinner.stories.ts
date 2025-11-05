import { Meta, StoryFn } from '@storybook/vue3';
import LoadingSpinner from './LoadingSpinner.vue';

export default {
  title: 'component/Indicators/LoadingSpinner',
  component: LoadingSpinner,
  tags: ['autodocs'],
  argTypes: {
    active: { control: 'boolean' },
  },
} as Meta<typeof LoadingSpinner>;

const Template: StoryFn<typeof LoadingSpinner> = (args) => ({
  components: { LoadingSpinner },
  setup() {
    return { args };
  },
  template: `<LoadingSpinner v-bind="args" />`,
});

export const Default = Template.bind({});
Default.args = {
  active: true,
};

export const Active = Template.bind({});
Active.args = {
  active: true,
};

export const Inactive = Template.bind({});
Inactive.args = {
  active: false,
};