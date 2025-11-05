import MultiselectList from './MultiselectList.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<MultiselectList> = {
  title: 'component/Lists/MultiselectList',
  component: MultiselectList,
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

const Template:StoryFn<MultiselectList> = (args) => ({
  Component:MultiselectList,
  props:args,
});

export const Default = Template.bind({});
Default.args = {
  items:[
    { id: '1', label: 'Option 1', selected: false },
    { id: '2', label: 'Option 2', selected: false },
    { id: '3', label: 'Option 3', selected: false }
  ],
  disabled:false,
};

export const ItemSelected = Template.bind({});
ItemSelected.args = {
  items:[
    { id: '1', label: 'Option 1', selected: true },
    { id: '2', label: 'Option 2', selected: false },
    { id: '3', label: 'Option 3', selected: false }
  ],
  disabled:false,
};

export const ItemDeselected = Template.bind({});
ItemDeselected.args = {
  items:[
    { id: '1', label: 'Option 1', selected: false },
    { id: '2', label: 'Option 2', selected: true },
    { id: '3', label: 'Option 3', selected: false }
  ],
  disabled:false,
};

export const Disabled = Template.bind({});
Disabled.args = {
  items:[
    { id: '1', label: 'Option 1', selected: false },
    { id: '2', label: 'Option 2', selected: false },
    { id: '3', label: 'Option 3', selected: false }
  ],
  disabled:true,
};

export const Hover = Template.bind({});
Hover.args = {
  items:[
    { id: '1', label: 'Option 1', selected: false },
    { id: '2', label: 'Option 2', selected: false },
    { id: '3', label: 'Option 3', selected: false }
  ],
  disabled:true,
};