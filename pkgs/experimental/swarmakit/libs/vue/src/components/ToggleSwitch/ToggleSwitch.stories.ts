import ToggleSwitch from './ToggleSwitch.vue';
import {Meta,StoryFn} from '@storybook/vue3'

export default {
  component: ToggleSwitch,
  title: 'component/Forms/ToggleSwitch',
  tags: ['autodocs'],
  argTypes: {
    checked: { control: { type: 'boolean' } },
    disabled: { control: { type: 'boolean' } },
  },
} as Meta<typeof ToggleSwitch>;

const Template:StoryFn<typeof ToggleSwitch> = (args) => ({
  components: { ToggleSwitch },
  setup() {
    return { args };
  },
  template: '<ToggleSwitch v-bind="args" />',
});

export const Default = Template.bind({});
Default.args = {
  checked: false,
  disabled: false,
};

export const On = Template.bind({});
On.args = {
  checked: true,
  disabled: false,
};

export const Off = Template.bind({});
Off.args = {
  checked: false,
  disabled: false,
};

export const Disabled = Template.bind({});
Disabled.args = {
  checked: false,
  disabled: true,
};