import { Meta, StoryFn } from '@storybook/vue3';
import CallButton from './CallButton.vue';

export default {
  title: 'component/Poker/CallButton',
  component: CallButton,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
  argTypes: {
    disabled: { control: 'boolean' },
  },
} as Meta<typeof CallButton>;

const Template: StoryFn<typeof CallButton> = (args) => ({
  components: { CallButton },
  setup() {
    return { args };
  },
  template: '<CallButton v-bind="args" />',
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