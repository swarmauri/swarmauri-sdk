import { Meta, StoryFn } from '@storybook/vue3';
import SearchBar from './SearchBar.vue';

export default {
  title: 'component/Input/SearchBar',
  component: SearchBar,
  tags: ['autodocs'],
  argTypes: {
    placeholder: {
      control: 'text',
    },
    isFocused: {
      control: 'boolean',
    },
    isDisabled: {
      control: 'boolean',
    },
  },
} as Meta<typeof SearchBar>;

const Template: StoryFn<typeof SearchBar> = (args) => ({
  components: { SearchBar },
  setup() {
    return { args };
  },
  template: `<SearchBar v-bind="args" />`,
});

export const Default = Template.bind({});
Default.args = {
  placeholder: 'Search...',
  isFocused: false,
  isDisabled: false,
};

export const Focused = Template.bind({});
Focused.args = {
  placeholder: 'Search...',
  isFocused: true,
  isDisabled: false,
};

export const Unfocused = Template.bind({});
Unfocused.args = {
  placeholder: 'Search...',
  isFocused: false,
  isDisabled: false,
};

export const Disabled = Template.bind({});
Disabled.args = {
  placeholder: 'Search...',
  isFocused: false,
  isDisabled: true,
};