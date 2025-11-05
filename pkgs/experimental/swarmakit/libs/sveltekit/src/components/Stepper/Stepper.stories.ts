import Stepper from './Stepper.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<Stepper> = {
  title: 'component/Indicators/Stepper',
  component: Stepper,
  tags: ['autodocs'],
  argTypes: {
    steps: { control: 'object' },
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

const Template:StoryFn<Stepper> = (args) => ({
  Component:Stepper,
  props:args,
});

export const Default = Template.bind({});
Default.args = {
  steps: [
    { label: 'Step 1', status: 'completed' },
    { label: 'Step 2', status: 'active' },
    { label: 'Step 3', status: 'disabled' },
  ],
};

export const Completed = Template.bind({});
Completed.args = {
  steps: [
    { label: 'Step 1', status: 'completed' },
    { label: 'Step 2', status: 'completed' },
    { label: 'Step 3', status: 'completed' },
  ],
};

export const Active = Template.bind({});
Active.args = {
  steps: [
    { label: 'Step 1', status: 'completed' },
    { label: 'Step 2', status: 'active' },
    { label: 'Step 3', status: 'disabled' },
  ],
};

export const Disabled = Template.bind({});
Disabled.args = {
  steps: [
    { label: 'Step 1', status: 'disabled' },
    { label: 'Step 2', status: 'disabled' },
    { label: 'Step 3', status: 'disabled' },
  ],
};