import StatusDots from './StatusDots.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<StatusDots> = {
  title: 'component/Indicators/StatusDots',
  component: StatusDots,
  tags: ['autodocs'],
  argTypes: {
    status: { control: 'select', options: ['online', 'offline', 'busy', 'idle'] },
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

const Template:StoryFn<StatusDots> = (args) => ({
  Component:StatusDots,
  props:args,
}); 

export const Default = Template.bind({});
Default.args = {
  status: 'offline',
};

export const Online = Template.bind({});
Online.args = {
  status: 'online',
};

export const Offline = Template.bind({});
Offline.args = {
  status: 'offline',
};

export const Busy = Template.bind({});
Busy.args = {
  status: 'busy',
};

export const Idle = Template.bind({});
Idle.args = {
  status: 'idle',
};