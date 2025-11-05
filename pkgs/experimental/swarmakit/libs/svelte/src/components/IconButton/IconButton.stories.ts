import IconButton from './IconButton.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<IconButton> = {
  title: 'component/Buttons/IconButton',
  component: IconButton,
  tags: ['autodocs'],
  argTypes: {
    icon: { control: 'text' },
    disabled: { control: 'boolean' },
    onClick: { action: 'clicked' },
  },
  parameters: {
    layout: 'centered',
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

const Template:StoryFn<IconButton> = (args) => ({
  Component:IconButton,
  props:args,
});

export const Default = Template.bind({});
Default.args = {
  icon: 'path/to/icon.svg',
  disabled: false,
  ariaLabel: 'Default Icon Button',
};

export const Active = Template.bind({});
Active.args = {
  icon: 'path/to/icon.svg',
  ariaLabel: 'Active Icon Button',
};

export const Hover = Template.bind({});
Hover.args = {
  icon: 'path/to/icon.svg',
  ariaLabel: 'Hover Icon Button',
};

export const Disabled = Template.bind({});
Disabled.args = {
  icon: 'path/to/icon.svg',
  disabled: true,
  ariaLabel: 'Disabled Icon Button',
};