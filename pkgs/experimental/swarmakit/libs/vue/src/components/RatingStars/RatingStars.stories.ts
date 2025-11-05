import { Meta, StoryFn } from '@storybook/vue3';
import RatingStars from './RatingStars.vue';

export default {
  title: 'component/Indicators/RatingStars',
  component: RatingStars,
  tags: ['autodocs'],
  argTypes: {
    maxStars: { control: 'number' },
    initialRating: { control: 'number' },
    inactive: { control: 'boolean' },
  },
} as Meta<typeof RatingStars>;

const Template: StoryFn<typeof RatingStars> = (args) => ({
  components: { RatingStars },
  setup() {
    return { args };
  },
  template: `<RatingStars v-bind="args" />`,
});

export const Default = Template.bind({});
Default.args = {
  maxStars: 5,
  initialRating: 0,
  inactive: false,
};

export const Hover = Template.bind({});
Hover.args = {
  maxStars: 5,
  initialRating: 0,
  inactive: false,
};

export const Selected = Template.bind({});
Selected.args = {
  maxStars: 5,
  initialRating: 3,
  inactive: false,
};

export const Inactive = Template.bind({});
Inactive.args = {
  maxStars: 5,
  initialRating: 3,
  inactive: true,
};