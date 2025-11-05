import { Meta, StoryFn } from '@storybook/vue3';
import FloatingActionButton from './FloatingActionButton.vue';

export default {
  title: 'component/Miscellaneous/FloatingActionButton',
  component: FloatingActionButton,
  tags: ['autodocs'],
} as Meta<typeof FloatingActionButton>;

const Template: StoryFn<typeof FloatingActionButton> = (args) => ({
  components: { FloatingActionButton },
  setup() {
    return { args };
  },
  template: '<FloatingActionButton v-bind="args" />',
});

export const Collapsed = Template.bind({});
Collapsed.args = { isExpanded: false };

export const Expanded = Template.bind({});
Expanded.args = { isExpanded: true };

export const Hover = Template.bind({});
Hover.args = {};