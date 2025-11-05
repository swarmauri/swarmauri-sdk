import ToggleSwitch from './ToggleSwitch.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<ToggleSwitch> = {
  title: 'component/Forms/ToggleSwitch',
  component: ToggleSwitch,
  tags: ['autodocs'],
  argTypes: {
    checked: { control: 'boolean' },
    disabled: { control: 'boolean' },
  },
  parameters: {
    layout: 'fullscreen',
    viewport: {
      viewports: {
        smallMobile: { name: 'Small Mobile', styles: { width: '320px', height: '568px' } },
        largeMobile: { name: 'Large Mobile', styles: { width: '414px', height: '896px' } },
        tablet: { name: 'Tablet', styles: { width: '768px', height: '1024px' } },
        desktop: { name: 'Desktop', styles: { width: '1024px', height: '768px' } },
      }
    }
  }
};

export default meta;

const Template:StoryFn<ToggleSwitch> = (args) => ({
  Component: ToggleSwitch,
  props:args
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