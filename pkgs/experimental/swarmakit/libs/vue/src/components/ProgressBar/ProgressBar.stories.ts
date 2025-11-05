import { Meta, StoryFn } from '@storybook/vue3';
import ProgressBar from './ProgressBar.vue';

export default {
  title: 'component/Indicators/ProgressBar',
  component: ProgressBar,
  tags: ['autodocs'],
  argTypes: {
    progress: { control: 'number' },
    disabled: { control: 'boolean' },
  },
} as Meta<typeof ProgressBar>;

const Template: StoryFn<typeof ProgressBar> = (args) => ({
  components: { ProgressBar },
  setup() {
    return { args };
  },
  template: `<ProgressBar v-bind="args" />`,
});

export const Default = Template.bind({});
Default.args = {
  progress: 50,
  disabled: false,
};

export const Complete = Template.bind({});
Complete.args = {
  progress: 100,
  disabled: false,
};

export const Incomplete = Template.bind({});
Incomplete.args = {
  progress: 0,
  disabled: false,
};

export const Hover = Template.bind({});
Hover.args = {
  progress: 70,
  disabled: false,
};

export const Disabled = Template.bind({});
Disabled.args = {
  progress: 50,
  disabled: true,
};