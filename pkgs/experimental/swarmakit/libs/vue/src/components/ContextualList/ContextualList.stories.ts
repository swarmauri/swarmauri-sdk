import { Meta, StoryFn } from '@storybook/vue3';
import ContextualList from './ContextualList.vue';

export default {
  title: 'component/Lists/ContextualList',
  component: ContextualList,
  tags: ['autodocs'],
  argTypes: {
    items: {
      control: 'object',
    },
  },
} as Meta<typeof ContextualList>;

const Template: StoryFn<typeof ContextualList> = (args) => ({
  components: { ContextualList },
  setup() {
    return { args };
  },
  template: `
    <ContextualList v-bind="args" />
  `,
});

export const Default = Template.bind({});
Default.args = {
  items: [
    { label: 'Item 1', actionTriggered: false, dismissed: false },
    { label: 'Item 2', actionTriggered: false, dismissed: false },
  ],
};

export const ActionTriggered = Template.bind({});
ActionTriggered.args = {
  items: [
    { label: 'Item 1', actionTriggered: true, dismissed: false },
    { label: 'Item 2', actionTriggered: false, dismissed: false },
  ],
};

export const Dismissed = Template.bind({});
Dismissed.args = {
  items: [
    { label: 'Item 1', actionTriggered: false, dismissed: true },
    { label: 'Item 2', actionTriggered: false, dismissed: false },
  ],
};