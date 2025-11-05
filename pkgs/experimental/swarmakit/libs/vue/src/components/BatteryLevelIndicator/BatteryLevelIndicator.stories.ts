import { Meta, StoryFn } from '@storybook/vue3';
import BatteryLevelIndicator from './BatteryLevelIndicator.vue';

export default {
  title: 'component/Indicators/BatteryLevelIndicator',
  component: BatteryLevelIndicator,
  tags: ['autodocs'],
  argTypes: {
    level: {
      control: { type: 'number', min: 0, max: 100 },
    },
    charging: {
      control: { type: 'boolean' },
    },
  },
} as Meta<typeof BatteryLevelIndicator>;

const Template: StoryFn<typeof BatteryLevelIndicator> = (args) => ({
  components: { BatteryLevelIndicator },
  setup() {
    return { args };
  },
  template: `<BatteryLevelIndicator v-bind="args" />`,
});

export const Default = Template.bind({});
Default.args = {
  level: 50,
  charging: false,
};

export const Charging = Template.bind({});
Charging.args = {
  level: 50,
  charging: true,
};

export const Full = Template.bind({});
Full.args = {
  level: 100,
  charging: false,
};

export const LowBattery = Template.bind({});
LowBattery.args = {
  level: 20,
  charging: false,
};

export const Critical = Template.bind({});
Critical.args = {
  level: 5,
  charging: false,
};