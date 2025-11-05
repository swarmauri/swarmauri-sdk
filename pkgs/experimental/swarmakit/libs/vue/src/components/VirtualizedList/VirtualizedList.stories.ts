import { Meta, StoryFn } from '@storybook/vue3';
import VirtualizedList from './VirtualizedList.vue';

export default {
  title: 'component/Lists/VirtualizedList',
  component: VirtualizedList,
  tags: ['autodocs'],
  argTypes: {
    items: { control: 'object' },
    itemHeight: { control: 'number' },
  },
} as Meta<typeof VirtualizedList>;

const Template: StoryFn<typeof VirtualizedList> = (args) => ({
  components: { VirtualizedList },
  setup() {
    return { args };
  },
  template: '<VirtualizedList v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  items: Array.from({ length: 100 }, (_, index) => ({ id: index, label: `Item ${index + 1}` })),
  itemHeight: 50,
};

export const LoadingMore = Template.bind({});
LoadingMore.args = {
  ...Default.args,
  items: Array.from({ length: 50 }, (_, index) => ({ id: index, label: `Item ${index + 1}` })),
};

export const EndOfList = Template.bind({});
EndOfList.args = {
  ...Default.args,
  items: Array.from({ length: 10 }, (_, index) => ({ id: index, label: `Item ${index + 1}` })),
};