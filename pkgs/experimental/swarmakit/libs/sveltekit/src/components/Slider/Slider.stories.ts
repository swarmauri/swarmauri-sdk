import Slider from './Slider.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<Slider> = {
  title: 'component/Input/Slider',
  component: Slider,
  tags: ['autodocs'],
  argTypes: {
    value: { control: 'number' },
    min: { control: 'number' },
    max: { control: 'number' },
    isDisabled: { control: 'boolean' },
    step: { control: 'number' }
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

const Template:StoryFn<Slider> = (args) => ({
  Component: Slider,
  props:args,
});

export const Default = Template.bind({});
Default.args = {
  value: 50,
  min: 0,
  max: 100,
  isDisabled: false,
  step: 1
};

export const Min = Template.bind({});
Min.args = {
  value: 0,
  min: 0,
  max: 100,
  isDisabled: false,
  step: 1
};

export const Max = Template.bind({});
Max.args = {
  value: 100,
  min: 0,
  max: 100,
  isDisabled: false,
  step: 1
};

export const Disabled = Template.bind({});
Disabled.args = {
  value: 50,
  min: 0,
  max: 100,
  isDisabled: true,
  step: 1
};