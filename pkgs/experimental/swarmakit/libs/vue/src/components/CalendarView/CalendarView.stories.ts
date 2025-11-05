import { Meta, StoryFn } from '@storybook/vue3';
import CalendarView from './CalendarView.vue';

export default {
  title: 'component/Scheduling/CalendarView',
  component: CalendarView,
  tags: ['autodocs'],
} as Meta<typeof CalendarView>;

const Template: StoryFn<typeof CalendarView> = (args) => ({
  components: { CalendarView },
  setup() {
    return { args };
  },
  template: '<CalendarView v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  currentView: 'month',
};

export const DayView = Template.bind({});
DayView.args = {
  currentView: 'day',
};

export const WeekView = Template.bind({});
WeekView.args = {
  currentView: 'week',
};

export const MonthView = Template.bind({});
MonthView.args = {
  currentView: 'month',
};

export const YearView = Template.bind({});
YearView.args = {
  currentView: 'year',
};

export const AgendaView = Template.bind({});
AgendaView.args = {
  currentView: 'agenda',
};