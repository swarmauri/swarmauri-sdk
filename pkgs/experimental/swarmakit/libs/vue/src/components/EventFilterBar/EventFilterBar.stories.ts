import { Meta, StoryFn } from '@storybook/vue3';
import EventFilterBar from './EventFilterBar.vue';

export default {
  title: 'component/Scheduling/EventFilterBar',
  component: EventFilterBar,
  tags: ['autodocs']
} as Meta<typeof EventFilterBar>;

const Template: StoryFn<typeof EventFilterBar> = (args) => ({
  components: { EventFilterBar },
  setup() {
    return { args };
  },
  template: '<EventFilterBar />',
});

export const Default = Template.bind({});
Default.args = {};


export const WithFilters = Template.bind({});
WithFilters.play = async ({ canvasElement }) => {
  const filterBar = canvasElement.querySelector('.event-filter-bar');
  if (filterBar) {
    const categorySelect = filterBar.querySelector('#category') as HTMLSelectElement;
    const locationInput = filterBar.querySelector('#location') as HTMLInputElement;
    
    if (categorySelect) {
      categorySelect.value = 'Conference';
      categorySelect.dispatchEvent(new Event('change'));
    }
    
    if (locationInput) {
      locationInput.value = 'New York';
      locationInput.dispatchEvent(new Event('input'));
    }
  }
};

export const Cleared = Template.bind({});
Cleared.play = async ({ canvasElement }) => {
  const filterBar = canvasElement.querySelector('.event-filter-bar');
  if (filterBar) {
    const clearButton = filterBar.querySelector('button[type="button"]') as HTMLButtonElement;
    if (clearButton) {
      clearButton.click();
    }
  }
};