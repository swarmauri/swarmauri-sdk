import SearchBar from './SearchBar.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<SearchBar> = {
  title: 'component/Input/SearchBar',
  component: SearchBar,
  tags: ['autodocs'],
  argTypes: {
    isFocused: { control: 'boolean' },
    isDisabled: { control: 'boolean' },
    placeholder: { control: 'text' }
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

const Template:StoryFn<SearchBar> = (args) => ({
  Component:SearchBar,
  props:args,
});

export const Default = Template.bind({});
Default.args = {
  isFocused: false,
  isDisabled: false,
  placeholder: 'Search...'
};

export const Focused = Template.bind({});
Focused.args = {
  isFocused: true,
  isDisabled: false,
  placeholder: 'Search...'
};

export const UnFocused = Template.bind({});
UnFocused.args = {
  isFocused: false,
  isDisabled: false,
  placeholder: 'Search...'
};

export const Disabled = Template.bind({});
Disabled.args = {
  isFocused: false,
  isDisabled: true,
  placeholder: 'Search...'
};