import SignalStrengthIndicator from './SignalStrengthIndicator.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<SignalStrengthIndicator> = {
  title: 'component/Indicators/SignalStrengthIndicator',
  component: SignalStrengthIndicator,
  tags: ['autodocs'],
  argTypes: {
    strength: { control: 'select', options: ['full', 'weak', 'none'] },
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

const Template:StoryFn<SignalStrengthIndicator> = (args) => ({
  Component:SignalStrengthIndicator,
  props:args,
}); 

export const Default = Template.bind({});
Default.args = {
  strength: 'none',
};

export const FullSignal = Template.bind({});
FullSignal.args = {
  strength: 'full',
};

export const WeakSignal = Template.bind({});
WeakSignal.args = {
  strength: 'weak',
};

export const NoSignal = Template.bind({});
NoSignal.args = {
  strength: 'none',
};