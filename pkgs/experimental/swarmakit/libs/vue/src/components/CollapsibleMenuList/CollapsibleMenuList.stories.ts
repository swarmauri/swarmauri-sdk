import { Meta, StoryFn } from '@storybook/vue3';
import CollapsibleMenuList from './CollapsibleMenuList.vue';

export default {
  title: 'component/Lists/CollapsibleMenuList',
  component: CollapsibleMenuList,
  tags: ['autodocs'],
  argTypes: {
    items: {
      control: 'object',
    },
  },
} as Meta<typeof CollapsibleMenuList>;

const Template: StoryFn<typeof CollapsibleMenuList> = (args) => ({
  components: { CollapsibleMenuList },
  setup() {
    return { args };
  },
  template: `
    <CollapsibleMenuList v-bind="args" />
  `,
});

export const Default = Template.bind({});
Default.args = {
  items: [
    { label: 'Menu Item 1', expanded: false, active: false, subItems: ['Sub Item 1', 'Sub Item 2'] },
    { label: 'Menu Item 2', expanded: false, active: false, subItems: ['Sub Item 1', 'Sub Item 2'] },
  ],
};

export const Expanded = Template.bind({});
Expanded.args = {
  items: [
    { label: 'Expanded Item', expanded: true, active: false, subItems: ['Sub Item 1', 'Sub Item 2'] },
  ],
};

export const Collapsed = Template.bind({});
Collapsed.args = {
  items: [
    { label: 'Collapsed Item', expanded: false, active: false, subItems: ['Sub Item 1', 'Sub Item 2'] },
  ],
};

export const Hover = Template.bind({});
Hover.args = {
  items: [
    { label: 'Hover Item', expanded: false, active: true, subItems: ['Sub Item 1', 'Sub Item 2'] },
  ],
};

export const Active = Template.bind({});
Active.args = {
  items: [
    { label: 'Active Item', expanded: false, active: true, subItems: ['Sub Item 1', 'Sub Item 2'] },
  ],
};