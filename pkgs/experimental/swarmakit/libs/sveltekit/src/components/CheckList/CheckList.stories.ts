import CheckList from './CheckList.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<CheckList> = {
  title: 'component/Lists/CheckList',
  component: CheckList,
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

const Template:StoryFn<CheckList>  = (args) => ({
  Component: CheckList,
  props: args,
});

export const Default = Template.bind({});
Default.args = {
  items : [
    { id: 1, label: 'Item 1' },
    { id: 2, label: 'Item 2' },
    { id: 3, label: 'Item 3' },
  ],
};

export const Checked = Template.bind({});
Checked.args = {
  items : [
    { id: 1, label: 'Item 1', checked:true, },
    { id: 2, label: 'Item 2', checked:false, },
    { id: 3, label: 'Item 3' , checked:true, },
  ],
};

export const UnChecked = Template.bind({});
UnChecked.args = {
  items : [
    { id: 1, label: 'Item 1', checked:false, },
    { id: 2, label: 'Item 2', checked:false, },
    { id: 3, label: 'Item 3' , checked:false, },
  ],
};

export const PartiallyChecked = Template.bind({});
PartiallyChecked.args = {
  items : [
    { id: 1, label: 'Item 1', partiallyChecked:true, },
    { id: 2, label: 'Item 2', partiallyChecked:false, },
    { id: 3, label: 'Item 3' , partiallyChecked:true, },
  ],
};

export const Disabled = Template.bind({});
Disabled.args = {
  items : [
    { id: 1, label: 'Item 1', disabled:true, },
    { id: 2, label: 'Item 2', disabled:false, },
    { id: 3, label: 'Item 3' , disabled:true, },
  ],
};