import ProgressCircle from './ProgressCircle.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<ProgressCircle> = {
  title: 'component/Indicators/ProgressCircle',
  component: ProgressCircle,
  tags: ['autodocs'],
  argTypes: {
    progress: { control: { type: 'range', min: 0, max: 100 } },
    state: { control: 'select', options: ['complete', 'incomplete', 'in-progress', 'paused', 'active'] },
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

const Template:StoryFn<ProgressCircle> = (args) => ({
  Component: ProgressCircle,
  props:args,
}); 

export const Default = Template.bind({});
Default.args = {
  progress: 50,
  state: 'in-progress',
};

export const Complete = Template.bind({});
Complete.args = {
  progress: 100,
  state: 'complete',
};

export const InComplete = Template.bind({});
InComplete.args = {
  progress: 0,
  state: 'incomplete',
};

export const InProgress = Template.bind({});
InProgress.args = {
  progress: 50,
  state: 'in-progress',
};

export const Paused = Template.bind({});
Paused.args = {
  progress: 50,
  state: 'paused',
};

export const Active = Template.bind({});
Active.args = {
  progress: 75,
  state: 'active',
};