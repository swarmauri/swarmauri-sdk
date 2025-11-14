const applyStyle = (element, style = {}) => {
  if (!element || !style) {
    return;
  }
  Object.entries(style).forEach(([key, value]) => {
    if (value == null) {
      return;
    }
    const cssKey = key.replace(/([A-Z])/g, '-$1').toLowerCase();
    element.style.setProperty(cssKey, String(value));
  });
};

const clearChildren = (element) => {
  if (!element) {
    return;
  }
  while (element.firstChild) {
    element.removeChild(element.firstChild);
  }
};

class BaseWidget {
  constructor({ target, props = {} }) {
    this.target = target || null;
    this.props = { ...props };
    this.root = this.createRoot();
    if (this.target && this.root) {
      this.target.appendChild(this.root);
    }
    this.render();
  }

  createRoot() {
    return document.createElement('div');
  }

  updateProps(props = {}) {
    if (!props) {
      return;
    }
    this.props = { ...this.props, ...props };
  }

  render() {}

  $set(props) {
    this.updateProps(props);
    this.render();
  }

  $destroy() {
    if (this.root && this.root.parentNode) {
      this.root.parentNode.removeChild(this.root);
    }
  }
}

export class CardbasedList extends BaseWidget {
  createRoot() {
    const root = document.createElement('div');
    root.className = 'le-cardbased-list';
    return root;
  }

  render() {
    if (!this.root) {
      return;
    }
    clearChildren(this.root);
    const { style = {}, cards = [], layout = {} } = this.props;
    applyStyle(this.root, style);
    const container = document.createElement('div');
    container.style.display = 'flex';
    container.style.flexDirection = 'column';
    container.style.gap = `${layout?.gap?.y ?? 16}px`;
    cards.forEach((card, idx) => {
      const cardEl = document.createElement('div');
      cardEl.className = 'le-cardbased-list__card';
      cardEl.style.display = 'flex';
      cardEl.style.flexDirection = 'column';
      cardEl.style.gap = '8px';
      cardEl.style.padding = `${layout?.padding?.y ?? 12}px ${layout?.padding?.x ?? 12}px`;
      cardEl.style.borderRadius = '12px';
      cardEl.style.background = 'rgba(15, 23, 42, 0.85)';
      const title = document.createElement('h3');
      title.textContent = card?.title ?? `Card ${idx + 1}`;
      title.style.margin = '0';
      title.style.fontSize = '1.1rem';
      const description = document.createElement('p');
      description.textContent = card?.description ?? '';
      description.style.margin = '0';
      description.style.opacity = '0.8';
      cardEl.appendChild(title);
      cardEl.appendChild(description);
      container.appendChild(cardEl);
    });
    this.root.appendChild(container);
  }
}

export class ActivityIndicators extends BaseWidget {
  createRoot() {
    const root = document.createElement('div');
    root.className = 'le-activity-indicator';
    root.style.display = 'flex';
    root.style.flexDirection = 'column';
    root.style.gap = '12px';
    return root;
  }

  render() {
    if (!this.root) {
      return;
    }
    clearChildren(this.root);
    const { style = {}, type = 'info', message = 'Waiting for realtime event…' } = this.props;
    applyStyle(this.root, style);
    const pill = document.createElement('div');
    pill.textContent = type.toUpperCase();
    pill.style.display = 'inline-flex';
    pill.style.alignItems = 'center';
    pill.style.justifyContent = 'center';
    pill.style.padding = '6px 12px';
    pill.style.borderRadius = '999px';
    pill.style.fontWeight = '600';
    pill.style.fontSize = '0.75rem';
    pill.style.background = 'rgba(37, 99, 235, 0.35)';
    const messageEl = document.createElement('div');
    messageEl.textContent = message;
    messageEl.style.fontSize = '0.95rem';
    messageEl.style.opacity = '0.85';
    this.root.appendChild(pill);
    this.root.appendChild(messageEl);
  }
}

export class DataSummary extends BaseWidget {
  createRoot() {
    const root = document.createElement('div');
    root.className = 'le-data-summary';
    root.style.display = 'grid';
    root.style.gridTemplateColumns = 'repeat(auto-fit, minmax(60px, 1fr))';
    root.style.gap = '12px';
    return root;
  }

  render() {
    if (!this.root) {
      return;
    }
    clearChildren(this.root);
    const { style = {}, data = [] } = this.props;
    applyStyle(this.root, style);
    data.forEach((value) => {
      const cell = document.createElement('div');
      cell.textContent = String(value);
      cell.style.display = 'flex';
      cell.style.alignItems = 'center';
      cell.style.justifyContent = 'center';
      cell.style.padding = '12px';
      cell.style.borderRadius = '12px';
      cell.style.background = 'rgba(15, 23, 42, 0.65)';
      cell.style.fontWeight = '600';
      this.root.appendChild(cell);
    });
  }
}

export default {
  CardbasedList,
  ActivityIndicators,
  DataSummary,
};
