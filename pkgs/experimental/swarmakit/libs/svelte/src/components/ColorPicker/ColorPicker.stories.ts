import ColorPicker from './ColorPicker.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<ColorPicker> = {
  title: 'component/Forms/ColorPicker',
  component: ColorPicker,
  tags: ['autodocs'],
  argTypes: {
    color: { control: 'color' },
    disabled: { control: 'boolean' },
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

const Template:StoryFn<ColorPicker> = (args) => ({
  Component: ColorPicker,
  props:args,
});

export const Default = Template.bind({});
Default.args = {
  'color': '#000000',
  disabled:false,
};

export const Selected = Template.bind({});
Selected.args = {
  color:'#ff5733',
  disabled:false,
};

export const Disabled = Template.bind({});
Disabled.args = {
  color:'#000000',
  disabled:true,
};