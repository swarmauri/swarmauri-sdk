import { Meta, StoryFn } from '@storybook/vue3';
import CommandPalette from './CommandPalette.vue';

export default {
  title: 'component/Miscellaneous/CommandPalette',
  component: CommandPalette,
  tags: ['autodocs'],
  argTypes: {
    isOpen: { control: 'boolean' },
  },
} as Meta<typeof CommandPalette>;

const Template: StoryFn<typeof CommandPalette> = (args) => ({
  components: { CommandPalette },
  setup() {
    return { args };
  },
  template: '<CommandPalette v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  isOpen: false,
};

export const Open = Template.bind({});
Open.args = {
  isOpen: true,
};

export const Closed = Template.bind({});
Closed.args = {
  isOpen: false,
};

export const ActiveSelection = Template.bind({});
ActiveSelection.args = {
  isOpen: true,
};