import NotificationBellIcon from './NotificationBellIcon.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<NotificationBellIcon> = {
  title: 'component/Indicators/NotificationBellIcon',
  component: NotificationBellIcon,
  tags: ['autodocs'],
  argTypes: {
    hasNotifications: { control: 'boolean' },
    dismissed: { control: 'boolean' },
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

const Template:StoryFn<NotificationBellIcon> = (args) => ({
  Component: NotificationBellIcon,
  props:args,
}); 

export const Default = Template.bind({});
Default.args = {
  hasNotifications:false,
  dismissed:false,
};

export const NoNotifications = Template.bind({});
NoNotifications.args = {
  hasNotifications:false,
  dismissed:true,
};

export const NewNotifications = Template.bind({});
NewNotifications.args = {
  hasNotifications:true,
  dismissed:false,
};

export const Dismissed = Template.bind({});
Dismissed.args = {
  hasNotifications:true,
  dismissed:true,
};