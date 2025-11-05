import Accordion from './Accordion.svelte';
import type { Meta,StoryFn } from '@storybook/svelte';

const meta: Meta<Accordion> = {
  title: 'component/Lists/Accordion',
  component: Accordion,
  tags: ['autodocs'],
  argTypes: {
    isOpen: { control: 'boolean' },
    title: { control: 'text' },
    content: { control: 'text' }
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
  Component: Accordion,
  props:args,
})

export const Default = Template.bind({});
Default.args = {
  isOpen:false,
  title:'Accordion Title',
  content:'Accordion content goes here.'
}

export const Open = Template.bind({});
Open.args = {
  isOpen:true,
  title:'Accordion Title',
  content:'Accordion content goes here.'
}

export const Closed = Template.bind({});
Closed.args = {
  isOpen:false,
  title:'Accordion Title',
  content:'Accordion content goes here.'
}

export const Hover = Template.bind({});
Hover.args = {
  isOpen:false,
  title: 'Accordion Title',
  content: 'Accordion content goes here.'
};
Hover.parameters = {
  pseudo:{hover:true}
}