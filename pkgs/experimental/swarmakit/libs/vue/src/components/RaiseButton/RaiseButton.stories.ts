import { Meta, StoryFn } from '@storybook/vue3';
import RaiseButton from './RaiseButton.vue';

export default {
  title: 'component/Poker/RaiseButton',
  component: RaiseButton,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
  argTypes: {
    disabled: { control: 'boolean' },
  },
} as Meta<typeof RaiseButton>;

const Template: StoryFn<typeof RaiseButton> = (args) => ({
  components: { RaiseButton },
  setup() {
    return { args };
  },
  template: '<RaiseButton v-bind="args" />',
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