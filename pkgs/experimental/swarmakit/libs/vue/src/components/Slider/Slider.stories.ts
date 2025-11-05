import { Meta, StoryFn } from '@storybook/vue3';
import Slider from './Slider.vue';

export default {
  title: 'component/Input/Slider',
  component: Slider,
  tags: ['autodocs'],
  argTypes: {
    min: {
      control: 'number',
    },
    max: {
      control: 'number',
    },
    value: {
      control: 'number',
    },
    step: {
      control: 'number',
    },
    isDisabled: {
      control: 'boolean',
    },
    showValue: {
      control: 'boolean',
    },
  },
} as Meta<typeof Slider>;

const Template: StoryFn<typeof Slider> = (args) => ({
  components: { Slider },
  setup() {
    return { args };
  },
  template: `<Slider v-bind="args" />`,
});

export const Default = Template.bind({});
Default.args = {
  min: 0,
  max: 100,
  value: 50,
  step: 1,
  isDisabled: false,
  showValue: true,
};

export const Min = Template.bind({});
Min.args = {
  min: 0,
  max: 100,
  value: 0,
  step: 1,
  isDisabled: false,
  showValue: true,
};

export const Max = Template.bind({});
Max.args = {
  min: 0,
  max: 100,
  value: 100,
  step: 1,
  isDisabled: false,
  showValue: true,
};

export const Disabled = Template.bind({});
Disabled.args = {
  min: 0,
  max: 100,
  value: 50,
  step: 1,
  isDisabled: true,
  showValue: true,
};