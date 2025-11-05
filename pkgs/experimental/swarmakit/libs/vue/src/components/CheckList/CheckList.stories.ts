import { Meta, StoryFn } from '@storybook/vue3';
import CheckList from './CheckList.vue';

export default {
  title: 'component/Lists/CheckList',
  component: CheckList,
  tags: ['autodocs'],
  argTypes: {
    items: {
      control: 'object',
    },
  },
} as Meta<typeof CheckList>;

const Template: StoryFn<typeof CheckList> = (args) => ({
  components: { CheckList },
  setup() {
    return { args };
  },
  template: `
    <CheckList v-bind="args" />
  `,
});

export const Default = Template.bind({});
Default.args = {
  items: [
    { label: 'Item 1', checked: false, indeterminate: false, disabled: false },
    { label: 'Item 2', checked: false, indeterminate: false, disabled: false },
  ],
};

export const Checked = Template.bind({});
Checked.args = {
  items: [
    { label: 'Checked Item', checked: true, indeterminate: false, disabled: false },
  ],
};

export const Unchecked = Template.bind({});
Unchecked.args = {
  items: [
    { label: 'Unchecked Item', checked: false, indeterminate: false, disabled: false },
  ],
};

export const PartiallyChecked = Template.bind({});
PartiallyChecked.args = {
  items: [
    { label: 'Partially Checked Item', checked: false, indeterminate: true, disabled: false },
  ],
};

export const Disabled = Template.bind({});
Disabled.args = {
  items: [
    { label: 'Disabled Item', checked: false, indeterminate: false, disabled: true },
  ],
};