import ScrollableList from './ScrollableList.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<ScrollableList> = {
  title: 'component/Lists/ScrollableList',
  component: ScrollableList,
  tags: ['autodocs'],
  argTypes: {
    items: { control: 'object' },
    disabled: { control: 'boolean' }
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

const Template:StoryFn<ScrollableList> = (args) => ({
  Component:ScrollableList,
  props:args,
});

export const Default = Template.bind({});
Default.args = {
  items: Array.from({ length: 20 }, (_, i) => ({ id: i + 1, text: `Item ${i + 1}` })),
  disabled: false
};

export const Scrolling = Template.bind({});
Scrolling.args = {
  items: Array.from({ length: 20 }, (_, i) => ({ id: i + 1, text: `Item ${i + 1}` })),
  disabled: false
};

export const EndOfList = Template.bind({});
EndOfList.args = {
  items: Array.from({ length: 5 }, (_, i) => ({ id: i + 1, text: `Item ${i + 1}` })),
  disabled: false
};

export const Hover = Template.bind({});
Hover.args = {
  items: Array.from({ length: 20 }, (_, i) => ({ id: i + 1, text: `Item ${i + 1}` })),
  disabled: false
};

export const Disabled = Template.bind({});
Disabled.args = {
  items: Array.from({ length: 20 }, (_, i) => ({ id: i + 1, text: `Item ${i + 1}` })),
  disabled: true
};