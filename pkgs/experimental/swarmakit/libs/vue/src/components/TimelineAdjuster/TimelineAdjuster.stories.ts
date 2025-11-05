import { Meta, StoryFn } from '@storybook/vue3';
import TimelineAdjuster from './TimelineAdjuster.vue';

export default {
  title: 'component/Scheduling/TimelineAdjuster',
  component: TimelineAdjuster,
  tags: ['autodocs']
} as Meta<typeof TimelineAdjuster>;

const Template: StoryFn<typeof TimelineAdjuster> = (args) => ({
  components: { TimelineAdjuster },
  setup() {
    return { args };
  },
  template: '<TimelineAdjuster v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {};

export const TimelineAdjusted = Template.bind({});
TimelineAdjusted.args = {
  feedbackMessage: 'Timeline adjusted to 3 hours view'
};

export const TimeRangeSet = Template.bind({});
TimeRangeSet.args = {
  feedbackMessage: 'Time range set to full day'
};