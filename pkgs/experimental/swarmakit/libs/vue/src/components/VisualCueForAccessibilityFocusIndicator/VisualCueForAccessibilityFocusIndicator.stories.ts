import { Meta, StoryFn } from '@storybook/vue3';
import VisualCueForAccessibilityFocusIndicator from './VisualCueForAccessibilityFocusIndicator.vue';

export default {
  title: 'component/Indicators/VisualCueForAccessibilityFocusIndicator',
  component: VisualCueForAccessibilityFocusIndicator,
  tags: ['autodocs'],
  argTypes: {
    label: {
      control: 'text',
    },
    isFocused: {
      control: 'boolean',
    },
  },
} as Meta<typeof VisualCueForAccessibilityFocusIndicator>;

const Template: StoryFn<typeof VisualCueForAccessibilityFocusIndicator> = (args) => ({
  components: { VisualCueForAccessibilityFocusIndicator },
  setup() {
    return { args };
  },
  template: `<VisualCueForAccessibilityFocusIndicator v-bind="args" />`,
});

export const Default = Template.bind({});
Default.args = {
  label: 'Focus me',
  isFocused: false,
};

export const Focused = Template.bind({});
Focused.args = {
  label: 'Focus me',
  isFocused: true,
};

export const Unfocused = Template.bind({});
Unfocused.args = {
  label: 'Focus me',
  isFocused: false,
};