import { Meta, StoryFn } from '@storybook/vue3';
import CardBadge from './CardBadge.vue';

export default {
  title: 'Component/Card Elements/CardBadge',
  component: CardBadge,
  tags: ['autodocs'],
  argTypes: {
    content: {
      control: { type: 'text' },
    },
    status: {
      control: { type: 'radio', options: ['default', 'active', 'inactive'] },
    },
  },
} as Meta;

const Template: StoryFn = (args) => ({
  components: { CardBadge },
  setup() {
    return { args };
  },
  template: '<CardBadge v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  content: 'Default Badge',
  status: 'default',
};

export const Active = Template.bind({});
Active.args = {
  content: 'Active Badge',
  status: 'active',
};

export const Inactive = Template.bind({});
Inactive.args = {
  content: 'Inactive Badge',
  status: 'inactive',
};

export const Hovered = Template.bind({});
Hovered.args = {
  content: 'Hovered Badge',
  status: 'default',
};