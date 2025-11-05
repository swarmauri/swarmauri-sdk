import SortableList from './SortableList.svelte';
import type { Meta, StoryFn} from '@storybook/svelte';

const meta: Meta = {
  title: 'Components/Lists/SortableList',
  component: SortableList,
  tags: ['autodocs'],
  argTypes: {
    items: {
      control: { type: 'object' },
    },
    disabled: {
      control: { type: 'boolean' },
    },
  },
};

export default meta;

const Template: StoryFn<SortableList> = (args) => ({
  Component: SortableList,
  props: args,
});

const sampleItems = ['Item 1', 'Item 2', 'Item 3', 'Item 4'];

export const Default = Template.bind({});
Default.args = {
  items: sampleItems,
  disabled: false,
};

export const Dragging = Template.bind({});
Dragging.args = {
  items: sampleItems,
  disabled: false,
};

export const Sorted = Template.bind({});
Sorted.args = {
  items: ['Item 2', 'Item 1', 'Item 3', 'Item 4'],
  disabled: false,
};

export const Disabled = Template.bind({});
Disabled.args = {
  items: sampleItems,
  disabled: true,
};