import type { Preview, addParameters } from "@storybook/vue3";
import '../src/themes/light.css';  // Load default light theme by default

export const globalTypes = {
  theme: {
    name: 'Theme',
    description: 'Global theme for components',
    defaultValue: 'light',
    toolbar: {
      icon: 'circlehollow',
      items: [
        { value: 'light', title: 'Light Theme' },
        { value: 'dark', title: 'Dark Theme' },
        { value: 'custom', title: 'Custom Theme' },
      ],
    },
  },
};

export const decorators = [
  (Story, context) => {
    const theme = context.globals.theme;
    
    // Dynamically load the CSS for the selected theme
    const link = document.getElementById('theme-style');
    if (link) {
      document.head.removeChild(link);
    }
    const style = document.createElement('link');
    style.id = 'theme-style';
    style.rel = 'stylesheet';
    style.href = `/src/themes/${theme}.css`;
    document.head.appendChild(style);
    
    // Set data-theme attribute for potential theme-based logic in CSS
    document.body.setAttribute('data-theme', theme);

    return {
      ...Story(),
    };
  },
];





const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
  },
};

export default preview;

