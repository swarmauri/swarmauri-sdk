import { userEvent, within } from '@storybook/test';
import NumberInputWithIncrement from './NumberInputWithIncrement.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<NumberInputWithIncrement> = {
  title: 'component/Forms/NumberInputWithIncrement',
  component: NumberInputWithIncrement,
  tags: ['autodocs'],
  argTypes: {
    value: { control: 'number' },
    min: { control: 'number' },
    max: { control: 'number' },
    step: { control: 'number' },
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

const Template:StoryFn<NumberInputWithIncrement> = (args) => ({
  Component:NumberInputWithIncrement,
  props:args,
});

export const Default = Template.bind({});
Default.args = {
  value: 0,
  min: 0,
  max: 100,
  step: 1,
  disabled: false,
};

export const Increment = Template.bind({});
Increment.args = {
  value: 5,
  min: 0,
  max: 10,
  step: 1,
  disabled: false,
};
Increment.play = async({canvasElement}) => {
  const canvas = within(canvasElement);

  const incrementButton = await canvas.getByText('+');

  await userEvent.click(incrementButton);
};

export const Decrement = Template.bind({});
Decrement.args = {
  value: 5,
  min: 0,
  max: 10,
  step: 1,
  disabled: false,
};
Decrement.play = async({canvasElement}) => {
  const canvas = within(canvasElement);

  const decrementButton = await canvas.getByText('-');
  await userEvent.click(decrementButton)
};

export const Disabled = Template.bind({});
Disabled.args = {
  value: 5,
  min: 0,
  max: 10,
  step: 1,
  disabled: true,
};