import { createLyla } from '@lylajs/web';

const { lyla } = createLyla({
  baseUrl: 'http://127.0.0.1:4242',
});

export { lyla };
