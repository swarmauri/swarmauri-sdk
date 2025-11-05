import InteractivePollResults from './InteractivePollResults.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<InteractivePollResults> = {
  title: 'component/Indicators/InteractivePollResults',
  component: InteractivePollResults,
  tags: ['autodocs'],
  argTypes: {
    options: { control: 'object' },
    totalVotes: { control: 'number' },
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

const Template:StoryFn<InteractivePollResults> = (args) => ({
  Component: InteractivePollResults,
  props:args,
});

export const Default = Template.bind({});
Default.args = {
  options: [
    { label: 'Option B', votes: 30 },
    { label: 'Option A', votes: 50 },
  ],
  totalVotes: 80,
};


export const LiveResults = Template.bind({});
LiveResults.args = {
  options: [
    { label: 'Option B', votes: 70 },
    { label: 'Option A', votes: 30 },
  ],
  totalVotes: 100,
};

export const Completed = Template.bind({});
Completed.args = {
  options: [
    { label: 'Option B', votes: 120 },
    { label: 'Option A', votes: 80 },
  ],
  totalVotes: 200,
};

export const Closed = Template.bind({});
Closed.args = {
  options: [
    { label: 'Option B', votes: 50 },
    { label: 'Option A', votes: 50 },
  ],
  totalVotes: 100,
};