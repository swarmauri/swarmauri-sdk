import RulerAndGuides from './RulerAndGuides.vue';
import { Meta, StoryFn } from '@storybook/vue3';

export default {
  title: 'component/Drawing/RulerAndGuides',
  component: RulerAndGuides,
  tags: ['autodocs'],
} as Meta;

const Template: StoryFn = (args) => ({
  components: { RulerAndGuides },
  setup() {
    return { args };
  },
  template: '<RulerAndGuides v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  guides: [],
};

export const GuideAdded = Template.bind({});
GuideAdded.args = {
  guides: [{ x: 50, y: 0 }],
};

export const GuideMoved = Template.bind({});
GuideMoved.args = {
  guides: [{ x: 100, y: 0 }],
};

export const GuideRemoved = Template.bind({});
GuideRemoved.args = {
  guides: [],
};