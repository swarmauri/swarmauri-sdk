import CountdownTimer from './CountdownTimer.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<CountdownTimer> = {
  title: 'component/Indicators/CountdownTimer',
  component: CountdownTimer,
  tags: ['autodocs'],
  argTypes: {
    duration: { control: 'number' },
    autoStart: { control: 'boolean' },
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

const Template:StoryFn<CountdownTimer> = (args) => ({
  Component: CountdownTimer,
  props: args,
});

export const Default = Template.bind({});
Default.args = {
  duration:60,
  autoStart:false,
};

export const Running = Template.bind({});
Running.args = {
  duration:60,
  autoStart:true,
};

export const Paused = Template.bind({});
Default.args = {
  duration:60,
  autoStart:false,
};

export const Completed = Template.bind({});
Completed.args = {
  duration:0,
  autoStart:false,
};