import { Meta, StoryFn } from '@storybook/vue3';
import PublicViewCalendar from './PublicViewCalendar.vue';

export default {
  title: 'component/Scheduling/PublicViewCalendar',
  component: PublicViewCalendar,
  tags: ['autodocs']
} as Meta<typeof PublicViewCalendar>;

const Template: StoryFn<typeof PublicViewCalendar> = (args) => ({
  components: { PublicViewCalendar },
  setup() {
    return { args };
  },
  template: '<PublicViewCalendar v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {};

export const ViewOnly = Template.bind({});
ViewOnly.args = {};

export const EventDetailsShown = Template.bind({});
EventDetailsShown.args = {
  selectedEventProp: {
    id: 1,
    title: 'Project Meeting',
    description: 'Discussing project scope.',
    category: 'Work',
    location: 'Room 101',
    date: '2023-11-01'
  }
};

export const FilterApplied = Template.bind({});
FilterApplied.args = {
  selectedCategoryProp: 'Work'
};