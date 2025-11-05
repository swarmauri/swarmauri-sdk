import { Meta, StoryFn } from '@storybook/vue3';
import Chips from './Chips.vue';

export default {
  title: 'component/Miscellaneous/Chips',
  component: Chips,
  tags: ['autodocs'],
  argTypes: {
    selectable: { control: 'boolean' },
    removable: { control: 'boolean' },
    grouped: { control: 'boolean' },
  },
} as Meta<typeof Chips>;

const Template: StoryFn<typeof Chips> = (args) => ({
  components: { Chips },
  setup() {
    return { args };
  },
  template: '<Chips v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  selectable: false,
  removable: false,
  grouped: false,
};

export const Selectable = Template.bind({});
Selectable.args = {
  selectable: true,
  removable: false,
  grouped: false,
};

export const Removable = Template.bind({});
Removable.args = {
  selectable: false,
  removable: true,
  grouped: false,
};

export const Grouped = Template.bind({});
Grouped.args = {
  selectable: false,
  removable: false,
  grouped: true,
};