import GroupedList from './GroupedList.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';
import {userEvent, within} from '@storybook/test';

const meta: Meta<GroupedList> = {
  title: 'component/Lists/GroupedList',
  component: GroupedList,
  tags: ['autodocs'],
  argTypes: {
    groups: { control: 'object' }
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

const Template:StoryFn<GroupedList> = (args) => ({
  Component: GroupedList,
  props:args,
});

export const Default = Template.bind({});
Default.args = {
  groups: [
    { title: 'Fruits', items: ['Apple', 'Banana', 'Cherry'], expanded: true },
    { title: 'Vegetables', items: ['Carrot', 'Lettuce', 'Peas'], expanded: false },
  ]
};

export const GroupExpanded = Template.bind({});
GroupExpanded.args = {
  groups: [
    { title: 'Fruits', items: ['Apple', 'Banana', 'Cherry'], expanded: true },
    { title: 'Vegetables', items: ['Carrot', 'Lettuce', 'Peas'], expanded: false },
  ]
};

export const GroupCollapsed = Template.bind({});
GroupCollapsed.args = {
  groups: [
    { title: 'Fruits', items: ['Apple', 'Banana', 'Cherry'], expanded: false },
    { title: 'Vegetables', items: ['Carrot', 'Lettuce', 'Peas'], expanded: false },
  ]
};

export const ItemHover = Template.bind({});
ItemHover.args = {
  groups: [
    { title: 'Fruits', items: ['Apple', 'Banana', 'Cherry'], expanded: true },
    { title: 'Vegetables', items: ['Carrot', 'Lettuce', 'Peas'], expanded: false },
  ]
};
ItemHover.play = async({canvasElement}) => {
  const canvas = within(canvasElement);
  const listItem = canvas.getByText('Banana');
  await userEvent.hover(listItem);
};

export const ItemSelected = Template.bind({});
ItemSelected.args = {
  groups: [
    { title: 'Fruits', items: ['Apple', 'Banana', 'Cherry'], expanded: true },
    { title: 'Vegetables', items: ['Carrot', 'Lettuce', 'Peas'], expanded: false },
  ]
};
ItemSelected.play = async({canvasElement}) => {
  const canvas = within(canvasElement);
  const listItem = canvas.getByText('Banana');
  await userEvent.click(listItem);
};