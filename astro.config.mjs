import { defineConfig } from 'astro/config';
import icon from 'astro-icon';
import tailwind from '@astrojs/tailwind';

// https://astro.build/config
export default defineConfig({
  site: 'https://neevs.io',
  // Custom domain deployment - no base path needed
  // All assets will be served from root
  integrations: [icon(), tailwind()],
});
