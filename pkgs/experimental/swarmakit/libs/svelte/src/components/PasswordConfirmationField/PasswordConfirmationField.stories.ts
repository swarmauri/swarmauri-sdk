import PasswordConfirmationField from './PasswordConfirmationField.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<PasswordConfirmationField> = {
  title: 'component/Forms/PasswordConfirmationField',
  component: PasswordConfirmationField,
  tags: ['autodocs'],
  argTypes: {
    password: { control: 'text' },
    confirmPassword: { control: 'text' },
    disabled: { control: 'boolean' },
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

const Template:StoryFn<PasswordConfirmationField> = (args) => ({
  Component: PasswordConfirmationField,
  props:args,
});

export const Default = Template.bind({});
Default.args = {
  password: '',
  confirmPassword: '',
  disabled: false,
};

export const Matching = Template.bind({});
Matching.args = {
  password: 'password123',
  confirmPassword: 'password123',
  disabled: false,
};

export const NotMatching = Template.bind({});
NotMatching.args = {
  password: 'password123',
  confirmPassword: 'password222',
  disabled: false,
};

export const Disabled = Template.bind({});
Disabled.args = {
  password: 'password123',
  confirmPassword: 'password123',
  disabled: true,
};