import CollapsibleMenuList from './CollapsibleMenuList.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<CollapsibleMenuList> = {
  title: 'component/Lists/CollapsibleMenuList',
  component: CollapsibleMenuList,
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

const Template:StoryFn<CollapsibleMenuList> = (args) => ({
  Component: CollapsibleMenuList,
  props: args,
});

export const Default = Template.bind({});
Default.args = {
  items: [
    { id: 1, label: 'Menu 1' },
    { id: 2, label: 'Menu 2' },
    { id: 3, label: 'Menu 3' }
  ],
};

export const Expanded = Template.bind({});
Expanded.args = {
  items: [
    { id: 1, label: 'Menu 1' , expanded:true , },
    { id: 2, label: 'Menu 2'},
    { id: 3, label: 'Menu 3', expanded:true ,},
  ],
};

export const Collapsed = Template.bind({});
Collapsed.args = {
  items: [
    { id: 1, label: 'Menu 1', expanded:false },
    { id: 2, label: 'Menu 2', expanded:false },
    { id: 3, label: 'Menu 3', expanded:false },
  ],
};

export const Hover = Template.bind({});
Hover.args = {
  items: [
    { id: 1, label: 'Menu 1' },
    { id: 2, label: 'Menu 2',expanded: true,},
    { id: 3, label: 'Menu 3' }
  ],
};


export const Active = Template.bind({});
Active.args = {
  items: [
    { id: 1, label: 'Menu 1', active:true,},
    { id: 2, label: 'Menu 2'},
    { id: 3, label: 'Menu 3'},
  ],
};