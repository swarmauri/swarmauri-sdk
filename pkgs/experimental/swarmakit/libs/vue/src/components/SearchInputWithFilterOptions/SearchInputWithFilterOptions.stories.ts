import SearchInputWithFilterOptions from './SearchInputWithFilterOptions.vue';
import {Meta, StoryFn} from '@storybook/vue3';

export default {
  component: SearchInputWithFilterOptions,
  title: 'component/Forms/SearchInputWithFilterOptions',
  tags: ['autodocs'],
  argTypes: {
    placeholder: { control: { type: 'text' } },
    disabled: { control: { type: 'boolean' } },
    filtersActive: { control: { type: 'boolean' } },
    noResults: { control: { type: 'boolean' } },
  },
} as Meta<typeof SearchInputWithFilterOptions>

const Template:StoryFn<typeof SearchInputWithFilterOptions> = (args) => ({
  components: { SearchInputWithFilterOptions },
  setup() {
    return { args };
  },
  template: '<SearchInputWithFilterOptions v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  placeholder: 'Search...',
  disabled: false,
  filtersActive: false,
  noResults: false,
};

export const Searching = Template.bind({});
Searching.args = {
  placeholder: 'Searching...',
  disabled: false,
  filtersActive: true,
  noResults: false,
};

export const FiltersActive = Template.bind({});
FiltersActive.args = {
  placeholder: 'Search...',
  disabled: false,
  filtersActive: true,
  noResults: false,
};

export const NoResults = Template.bind({});
NoResults.args = {
  placeholder: 'Search...',
  disabled: false,
  filtersActive: false,
  noResults: true,
};

export const Disabled = Template.bind({});
Disabled.args = {
  placeholder: 'Search...',
  disabled: true,
  filtersActive: false,
  noResults: false,
};