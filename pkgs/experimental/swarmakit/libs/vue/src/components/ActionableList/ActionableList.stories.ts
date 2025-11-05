import { Meta, StoryFn } from '@storybook/vue3';
import ActionableList from './ActionableList.vue';

export default {
  title: 'component/Lists/ActionableList',
  component: ActionableList,
  tags: ['autodocs'],
  argTypes: {
    items: {
      control: 'object',
    },
  },
} as Meta<typeof ActionableList>;

const Template: StoryFn<typeof ActionableList> = (args) => ({
  components: { ActionableList },
  setup() {
    return { args };
  },
  template: `
    <ActionableList v-bind="args" />
  `,
});

export const Default = Template.bind({});
Default.args = {
  items: [
    { label: 'Item 1', actionLabel: 'Action', disabled: false, loading: false },
    { label: 'Item 2', actionLabel: 'Action', disabled: false, loading: false },
    { label: 'Item 3', actionLabel: 'Action', disabled: false, loading: false },
  ],
};

export const Hover = Template.bind({});
Hover.args = {
  items: [
    { label: 'Hover over me', actionLabel: 'Action', disabled: false, loading: false },
  ],
};

export const ActionTriggered = Template.bind({});
ActionTriggered.args = {
  items: [
    { label: 'Item with action triggered', actionLabel: 'Action', disabled: false, loading: false },
  ],
};

export const Disabled = Template.bind({});
Disabled.args = {
  items: [
    { label: 'Disabled Item', actionLabel: 'Action', disabled: true, loading: false },
  ],
};

export const Loading = Template.bind({});
Loading.args = {
  items: [
    { label: 'Loading Item', actionLabel: 'Action', disabled: false, loading: true },
  ],
};