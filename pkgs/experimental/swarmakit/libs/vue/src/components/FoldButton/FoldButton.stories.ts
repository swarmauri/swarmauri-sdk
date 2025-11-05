import { Meta, StoryFn } from '@storybook/vue3';
import FoldButton from './FoldButton.vue';

export default {
  title: 'component/Poker/FoldButton',
  component: FoldButton,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
  argTypes: {
    disabled: { control: 'boolean' },
  },
} as Meta<typeof FoldButton>;

const Template: StoryFn<typeof FoldButton> = (args) => ({
  components: { FoldButton },
  setup() {
    return { args };
  },
  template: '<FoldButton v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  disabled: false,
};

export const Hovered = Template.bind({});
Hovered.args = {
  disabled: false,
};

export const Disabled = Template.bind({});
Disabled.args = {
  disabled: true,
};