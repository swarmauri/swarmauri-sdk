import { Meta, StoryFn } from '@storybook/vue3';
import SearchWithAutocomplete from './SearchWithAutocomplete.vue';

export default {
  title: 'component/Miscellaneous/SearchWithAutocomplete',
  component: SearchWithAutocomplete,
  tags: ['autodocs'],
} as Meta<typeof SearchWithAutocomplete>;

const Template: StoryFn<typeof SearchWithAutocomplete> = (args) => ({
  components: { SearchWithAutocomplete },
  setup() {
    return { args };
  },
  template: '<SearchWithAutocomplete v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = { options: ['Apple', 'Banana', 'Cherry', 'Date', 'Fig', 'Grape'] };

export const Typing = Template.bind({});
Typing.args = { options: ['Apple', 'Banana', 'Cherry'], query: 'Ap' };

export const ShowingResults = Template.bind({});
ShowingResults.args = { options: ['Apple', 'Banana', 'Cherry'], query: 'B' };

export const NoResults = Template.bind({});
NoResults.args = { options: ['Apple', 'Banana', 'Cherry'], query: 'Xylophone' };