import Textarea from './Textarea.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<Textarea> = {
  title: 'component/Forms/Textarea',
  component: Textarea,
  tags: ['autodocs'],
  argTypes: {
    value: { control: 'text' },
    disabled: { control: 'boolean' },
  },
  parameters: {
    layout: 'fullscreen',
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

const Template:StoryFn<Textarea> = (args) => ({
  Component:Textarea,
  props:args,
}); 

export const Default = Template.bind({});
Default.args = {
  value: '',
  disabled: false,
};

export const Disabled = Template.bind({});
Disabled.args = {
  value:'This textarea is disabled',
  disabled: true,
};