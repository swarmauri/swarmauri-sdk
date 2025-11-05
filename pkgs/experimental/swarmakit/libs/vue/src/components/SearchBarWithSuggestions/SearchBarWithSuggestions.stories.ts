import SearchBarWithSuggestions from './SearchBarWithSuggestions.vue';
import {Meta,StoryFn} from '@storybook/vue3'

export default {
  title: 'components/Data/SearchBarWithSuggestions',
  component: SearchBarWithSuggestions,
  tags: ['autodocs'],
} as Meta<typeof SearchBarWithSuggestions>

const Template:StoryFn<typeof SearchBarWithSuggestions> = (args) => ({
  components: { SearchBarWithSuggestions },
  setup() {
    return { args };
  },
  template: '<SearchBarWithSuggestions v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  suggestions: ['apple', 'banana', 'grape', 'orange', 'strawberry'],
};

export const Searching = Template.bind({});
Searching.args = {
  ...Default.args,
};

export const SuggestionsVisible = Template.bind({});
SuggestionsVisible.args = {
  ...Default.args,
  suggestions: ['apple', 'apricot', 'avocado'],
};

export const NoResults = Template.bind({});
NoResults.args = {
  ...Default.args,
  suggestions: [],
};