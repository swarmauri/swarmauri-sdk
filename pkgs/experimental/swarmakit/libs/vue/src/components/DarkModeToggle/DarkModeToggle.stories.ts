import { Meta, StoryFn } from '@storybook/vue3';
import DarkModeToggle from './DarkModeToggle.vue';

export default {
  title: 'component/Miscellaneous/DarkModeToggle',
  component: DarkModeToggle,
  tags: ['autodocs'],
} as Meta<typeof DarkModeToggle>;

const Template: StoryFn<typeof DarkModeToggle> = (args) => ({
  components: { DarkModeToggle },
  setup() {
    return { args };
  },
  template: '<DarkModeToggle v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {};

export const LightMode = Template.bind({});
LightMode.args = {};

export const DarkMode = Template.bind({});
DarkMode.args = {};