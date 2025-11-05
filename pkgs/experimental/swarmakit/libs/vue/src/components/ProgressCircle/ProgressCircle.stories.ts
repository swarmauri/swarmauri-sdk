import { Meta, StoryFn } from '@storybook/vue3';
import ProgressCircle from './ProgressCircle.vue';

export default {
  title: 'component/Indicators/ProgressCircle',
  component: ProgressCircle,
  tags: ['autodocs'],
  argTypes: {
    progress: { control: 'number' },
    status: { control: 'select', options: ['complete', 'incomplete', 'paused', 'active'] },
  },
} as Meta<typeof ProgressCircle>;

const Template: StoryFn<typeof ProgressCircle> = (args) => ({
  components: { ProgressCircle },
  setup() {
    return { args };
  },
  template: `<ProgressCircle v-bind="args" />`,
});

export const Default = Template.bind({});
Default.args = {
  progress: 50,
  status: 'active',
};

export const Complete = Template.bind({});
Complete.args = {
  progress: 100,
  status: 'complete',
};

export const Incomplete = Template.bind({});
Incomplete.args = {
  progress: 0,
  status: 'incomplete',
};

export const Paused = Template.bind({});
Paused.args = {
  progress: 50,
  status: 'paused',
};

export const Active = Template.bind({});
Active.args = {
  progress: 50,
  status: 'active',
};