import PinnedList from './PinnedList.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<PinnedList> = {
  title: 'component/Lists/PinnedList',
  component: PinnedList,
  tags: ['autodocs'],
  argTypes: {
    items: { control: 'object' },
    selectedItem: { control: 'number' }
  },
  parameters: {
    layout: 'centered',
    viewport: {
      viewports: {
        smallMobile: { name: 'Small Mobile', styles: { width: '320px', height: '568px' } },
        largeMobile: { name: 'Large Mobile', styles: { width: '414px', height: '896px' } },
        tablet: { name: 'Tablet', styles: { width: '768px', height: '1024px' } },
        desktop: { name: 'Desktop', styles: { width: '1024px', height: '768px' } },
      }
    }
  }
};

export default meta;

const Template:StoryFn<PinnedList> = (args) => ({
  Component: PinnedList,
  props: args,
}); 

export const Default = Template.bind({});
Default.args = {
  items: [
    { id: 1, text: 'Item 1', pinned: false },
    { id: 2, text: 'Item 2', pinned: false },
    { id: 3, text: 'Item 3', pinned: false }
  ],
  selectedItem: null
};

export const Pinned = Template.bind({});
Pinned.args = {
  items: [
    { id: 1, text: 'Item 1', pinned: true },
    { id: 2, text: 'Item 2', pinned: false },
    { id: 3, text: 'Item 3', pinned: false }
  ],
  selectedItem: null
};

export const Unpinned = Template.bind({});
Unpinned.args = {
  items: [
    { id: 1, text: 'Item 1', pinned: false },
    { id: 2, text: 'Item 2', pinned: false },
    { id: 3, text: 'Item 3', pinned: false }
  ],
  selectedItem: null
};


export const Hover = Template.bind({});
Hover.args = {
  items: [
    { id: 1, text: 'Item 1', pinned: false },
    { id: 2, text: 'Item 2', pinned: false },
    { id: 3, text: 'Item 3', pinned: false }
  ],
  selectedItem: null
};

export const selectedItem = Template.bind({});
selectedItem.args = {
  items: [
    { id: 1, text: 'Item 1', pinned: false },
    { id: 2, text: 'Item 2', pinned: false },
    { id: 3, text: 'Item 3', pinned: false }
  ],
  selectedItem: 2,
};