import CardbasedList from './CardbasedList.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<CardbasedList> = {
  title: 'component/Lists/CardbasedList',
  component: CardbasedList,
  tags: ['autodocs'],
  argTypes: {
    cards: { control: 'object' }
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

const Template:StoryFn<CardbasedList> = (args) => ({
  Component:CardbasedList,
  props:args,
});

export const Default = Template.bind({});
Default.args = {
  cards: [
    { id: 1, title: 'Card 1', description: 'This is card 1 description' },
    { id: 2, title: 'Card 2', description: 'This is card 2 description' },
    { id: 3, title: 'Card 3', description: 'This is card 3 description' }, 
  ]
};

export const Hover = Template.bind({});
Hover.args = {
  cards: [
    { id: 1, title: 'Card 1', description: 'This is card 1 description' },
    { id: 2, title: 'Card 2', description: 'This is card 2 description' },
    { id: 3, title: 'Card 3', description: 'This is card 3 description' }, 
  ]
};
Hover.parameters = {
  pseudo: {hover:true},
};

export const Selected = Template.bind({});
Selected.args = {
  cards: [
    { id: 1, title: 'Card 1', description: 'This is card 1 description', selected:true, },
    { id: 2, title: 'Card 2', description: 'This is card 2 description', selected:false,},
    { id: 3, title: 'Card 3', description: 'This is card 3 description', selected:true, }, 
  ]
};

export const Disabled = Template.bind({});
Disabled.args = {
  cards: [
    { id: 1, title: 'Card 1', description: 'This is card 1 description', disabled:true, },
    { id: 2, title: 'Card 2', description: 'This is card 2 description', disabled:false,},
    { id: 3, title: 'Card 3', description: 'This is card 3 description', disabled:true, }, 
  ]
};