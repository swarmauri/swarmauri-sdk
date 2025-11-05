import Button from './Button.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<Button> = {
  title: 'component/Buttons/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    label: { control: 'text' },
    type: { control: 'select', options: ['primary', 'secondary'] },
    disabled: { control: 'boolean' },
    onClick: { action: 'clicked' },
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

const Template:StoryFn<Button> = (args) => ({
  Component:Button,
  props:args,
});

export const Default = Template.bind({});
Default.args = {
  label:'Button',
  type:'primary',
  disabled:false,
};

export const Primary = Template.bind({});
Primary.args = {
  label:'Primary Button',
  type:'primary',
  disabled:false,
};

export const Secondary = Template.bind({});
Secondary.args = {
  label:'Secondary Button',
  type:'secondary',
  disabled:false,
};

export const Disabled = Template.bind({});
Disabled.args = {
  label:'Disabled Button',
  disabled:true,
};

export const Hover = Template.bind({});
Hover.args = {
  label:'Hover Button',
};

export const Active = Template.bind({});
Active.args = {
  label:'Active Button',
};