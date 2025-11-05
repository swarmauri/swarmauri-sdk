import LoadingSpinner from './LoadingSpinner.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<LoadingSpinner> = {
  title: 'component/Indicators/LoadingSpinner',
  component: LoadingSpinner,
  tags: ['autodocs'],
  argTypes: {
    active: { control: 'boolean' },
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

const Template:StoryFn<LoadingSpinner> = (args) => ({
  Component: LoadingSpinner,
  props:args,
}); 

export const Default = Template.bind({});
Default.args = {
  active:true,
};

export const Active = Template.bind({});
Active.args = {
  active:true,
};

export const Inactive = Template.bind({});
Inactive.args = {
  active:false,
};