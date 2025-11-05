import Pagination from './Pagination.svelte';
import type { Meta, StoryFn } from '@storybook/svelte';

const meta: Meta<Pagination> = {
  title: 'component/Lists/Pagination',
  component: Pagination,
  tags: ['autodocs'],
  argTypes: {
    totalItems: { control: 'number' },
    itemsPerPage: { control: 'number' },
    currentPage: { control: 'number' }
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

const Template:StoryFn<Pagination> = (args) => ({
  Component: Pagination,
  props:args,
});

export const Default = Template.bind({});
Default.args = {
  totalItems: 50,
  itemsPerPage: 10,
  currentPage: 1 
};

export const Active = Template.bind({});
Active.args = {
  totalItems: 50,
  itemsPerPage: 10,
  currentPage: 3
};

export const Inactive = Template.bind({});
Inactive.args = {
  totalItems: 50,
  itemsPerPage: 10,
  currentPage: 1
};

export const Hover = Template.bind({});
Hover.args = {
  totalItems: 50,
  itemsPerPage: 10,
  currentPage: 2
};