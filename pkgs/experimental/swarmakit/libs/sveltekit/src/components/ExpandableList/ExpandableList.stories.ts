import ExpandableList from './ExpandableList.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';
import { userEvent, within } from '@storybook/test';

const meta: Meta<ExpandableList> = {
  title: 'component/Lists/ExpandableList',
  component: ExpandableList,
  tags: ['autodocs'],
  argTypes: {
    items: { control: 'object' }
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

const Template:StoryFn<ExpandableList> = (args) => ({
  Component:ExpandableList,
  props:args,
});

export const Default = Template.bind({});
Default.args = {
  items: [
    { id: '1', label: 'Item 1', content: 'Content of Item 1' },
    { id: '2', label: 'Item 2', content: 'Content of Item 2' },
    { id: '3', label: 'Item 3', content: 'Content of Item 3' }
  ]
};

export const ItemExpanded = Template.bind({});
ItemExpanded.args = {
  items: [
    { id: '1', label: 'Item 1', content: 'Content of Item 1' },
    { id: '2', label: 'Item 2', content: 'Content of Item 2' },
    { id: '3', label: 'Item 3', content: 'Content of Item 3' }
  ]
};
ItemExpanded.play = async({canvasElement}) => {
  const canvas = within(canvasElement);
  const firstItem = await canvas.getByText('Item 1');
  await userEvent.click(firstItem);

};

export const ItemCollapsed = Template.bind({});
ItemCollapsed.args = {
  items:[
    { id: '1', label: 'Item 1', content: 'Content of Item 1' },
    { id: '2', label: 'Item 2', content: 'Content of Item 2' },
    { id: '3', label: 'Item 3', content: 'Content of Item 3' },
  ],
};

export const Hover = Template.bind({});
Hover.args = {
  items: [
    { id: '1', label: 'Item 1', content: 'Content of Item 1' },
    { id: '2', label: 'Item 2', content: 'Content of Item 2' },
    { id: '3', label: 'Item 3', content: 'Content of Item 3' }
  ]
}
Hover.play = async({canvasElement}) => {
  const canvas = within(canvasElement);
  const firstItem = canvas.getByText('Item 1')
  await userEvent.hover(firstItem);
};

export const Selected = Template.bind({});
Selected.args = {
  items: [
    { id: '1', label: 'Item 1', content: 'Content of Item 1' },
    { id: '2', label: 'Item 2', content: 'Content of Item 2' },
    { id: '3', label: 'Item 3', content: 'Content of Item 3' }
  ],
};
Selected.play = async({canvasElement}) => {
  const canvas = within(canvasElement);
  const secondItem = await canvas.getByText('Item 2');
  await userEvent.click(secondItem);
};