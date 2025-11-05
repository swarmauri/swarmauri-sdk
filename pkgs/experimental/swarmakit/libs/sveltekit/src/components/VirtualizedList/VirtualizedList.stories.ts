import VirtualizedList from './VirtualizedList.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta = {
  title: 'Components/Lists/VirtualizedList',
  component: VirtualizedList,
  tags: ['autodocs'],
  argTypes: {
    items: {
      control: { type: 'object' },
    },
    isLoading: {
      control: { type: 'boolean' },
    },
    hasMore: {
      control: { type: 'boolean' },
    },
    loadMore: { action: 'loadMore' },
  },
};

export default meta;

const Template: StoryFn<VirtualizedList> = (args) => ({
  Component: VirtualizedList,
  props: args,
});

const sampleItems = Array.from({ length: 20 }, (_, i) => `Item ${i + 1}`);

export const Default = Template.bind({});
Default.args = {
  items: sampleItems,
  isLoading: false,
  hasMore: true,
  loadMore: () => console.log('Loading more items...'),
};

export const LoadingMore = Template.bind({});
LoadingMore.args = {
  items: sampleItems,
  isLoading: true,
  hasMore: true,
  loadMore: () => console.log('Loading more items...'),
};

export const EndOfList = Template.bind({});
EndOfList.args = {
  items: sampleItems,
  isLoading: false,
  hasMore: false,
  loadMore: () => console.log('Loading more items...'),
};