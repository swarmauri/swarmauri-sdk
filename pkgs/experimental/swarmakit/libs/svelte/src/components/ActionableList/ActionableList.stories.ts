import ActionableList from './ActionableList.svelte';
import type { Meta,StoryFn } from '@storybook/svelte';

const meta: Meta<ActionableList> = {
  title: 'component/Lists/ActionableList',
  component: ActionableList,
  tags: ['autodocs'],
  argTypes: {
    items: { control: 'object' },
    loading: { control: 'boolean' }
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

const Template:StoryFn = (args) => ({
  Component:ActionableList,
  props:args,
});

export const Default = Template.bind({});
Default.args = {
  items:[
    {id:1, text:'Item 1', action:()=> alert('Action 1 triggered')},
    {id:2, text:'Item 2', action:()=> alert('Action 2 triggered')},
    {id:3, text:'Item 3', action:()=> alert('Action 3 triggered')},
  ],
  loading:false,
};

export const Hover = Template.bind({});
Hover.args = {
  items:[
    {id:1, text:'Item 1', action:()=> alert('Action 1 triggered')},
    {id:2, text:'Item 2', action:()=> alert('Action 2 triggered')},
    {id:3, text:'Item 3', action:()=> alert('Action 3 triggered')},
  ],
  loading:false,
};
Hover.parameters = {
  pseudo: {hover:true},
}

export const ActionTriggered = Template.bind({});
ActionTriggered.args = {
  items:[
    {id:1, text:'Item 1', action:()=> alert('Action 1 triggered')},
    {id:2, text:'Item 2', action:()=> alert('Action 2 triggered')},
    {id:3, text:'Item 3', action:()=> alert('Action 3 triggered')},
  ],
  loading:false,
}

export const Disabled = Template.bind({});
Disabled.args = {
  items:[
    {id:1, text:'Item 1', action:()=> alert('Action 1 triggered'),disabled:true},
    {id:2, text:'Item 2', action:()=> alert('Action 2 triggered'),disabled:true},
    {id:3, text:'Item 3', action:()=> alert('Action 3 triggered'),disabled:true},
  ],
  loading:false,
};

export const Loading = Template.bind({});
Loading.args = {
  items:[
    {id:1, text:'Item 1', action:()=> alert('Action 1 triggered')},
    {id:2, text:'Item 2', action:()=> alert('Action 2 triggered')},
    {id:3, text:'Item 3', action:()=> alert('Action 3 triggered')},
  ],
  loading:false,
}