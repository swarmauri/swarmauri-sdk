import DateAndTimePicker from './DateAndTimePicker.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<DateAndTimePicker> = {
  title: 'component/Forms/DateAndTimePicker',
  component: DateAndTimePicker,
  tags: ['autodocs'],
  argTypes: {
    date: { control: 'date' },
    time: { control: 'text' },
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

const Template:StoryFn<DateAndTimePicker> = (args) => ({
  Component: DateAndTimePicker,
  props: args,
});

export const Default = Template.bind({});
Default.args = {
  date: '',
  time: '',
  disabled:false,
};

export const DateSelected = Template.bind({});
DateSelected.args = {
  date: '2023-10-01',
  time: '',
  disabled:false,
};

export const TimeSelected = Template.bind({});
TimeSelected.args = {
  date: '',
  time: '12:00',
  disabled:false,
};

export const Disabled = Template.bind({});
Disabled.args = {
  date: '',
  time: '',
  disabled:true,
};