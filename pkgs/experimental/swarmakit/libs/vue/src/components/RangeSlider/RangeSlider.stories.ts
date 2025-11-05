import RangeSlider from './RangeSlider.vue';
import {Meta,StoryFn} from '@storybook/vue3'

export default {
  component: RangeSlider,
  title: 'component/Forms/RangeSlider',
  tags: ['autodocs'],
  argTypes: {
    min: { control: { type: 'number' } },
    max: { control: { type: 'number' } },
    value: { control: { type: 'number' } },
    step: { control: { type: 'number' } },
    disabled: { control: { type: 'boolean' } },
    label: { control: { type: 'text' } },
    labelPosition: { 
      control: { type: 'select', options: ['left', 'center', 'right'] }
    },
  },
} as Meta<typeof RangeSlider>

const Template:StoryFn<typeof RangeSlider> = (args) => ({
  components: { RangeSlider },
  setup() {
    return { args };
  },
  template: '<RangeSlider v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  min: 0,
  max: 100,
  value: 50,
  step: 1,
  disabled: false,
  label: 'Volume',
  labelPosition: 'right',
};

export const Min = Template.bind({});
Min.args = {
  ...Default.args,
  value: 0,
};

export const Max = Template.bind({});
Max.args = {
  ...Default.args,
  value: 100,
};

export const Hover = Template.bind({});
Hover.parameters = {
  pseudo: { hover: true },
};
Hover.args = {
  ...Default.args,
};

export const Active = Template.bind({});
Active.parameters = {
  pseudo: { active: true },
};
Active.args = {
  ...Default.args,
};

export const Disabled = Template.bind({});
Disabled.args = {
  ...Default.args,
  disabled: true,
};