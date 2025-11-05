import LoadMoreButtonInList from './LoadmorebuttoninList.svelte'
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<LoadMoreButtonInList> = {
  title: 'component/Lists/LoadMoreButtonInList',
  component: LoadMoreButtonInList,
  tags: ['autodocs'],
  argTypes: {
    items: { control: 'object' },
    loadMore: { action: 'loadMore' },
    isLoading: { control: 'boolean' },
    isEndOfList: { control: 'boolean' }
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

const Template:StoryFn<LoadMoreButtonInList> = (args) => ({
  Component: LoadMoreButtonInList,
  props: args,
});

export const Default  = Template.bind({});
Default.args = {
    items: ['Item 1', 'Item 2', 'Item 3'],
    isLoading: false,
    isEndOfList: false
};

export const Loading  = Template.bind({});
Loading.args = {
    items: ['Item 1', 'Item 2', 'Item 3'],
    isLoading: true,
    isEndOfList: false
};

export const EndOfList  = Template.bind({});
EndOfList.args = {
    items: ['Item 1', 'Item 2', 'Item 3'],
    isLoading: false,
    isEndOfList: true
};