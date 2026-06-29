import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { viteExternalsPlugin } from 'vite-plugin-externals';

const externalLibs: Record<string, string> = {
  react: 'React',
  'react-dom': 'ReactDOM',
  '@mantine/core': 'MantineCore',
  '@mantine/notifications': 'MantineNotifications',
};

export default defineConfig({
  plugins: [
    react({ jsxRuntime: 'classic' }),
    viteExternalsPlugin(externalLibs),
  ],
  build: {
    minify: true,
    cssCodeSplit: false,
    rollupOptions: {
      preserveEntrySignatures: 'exports-only',
      input: ['./src/LayoutsPanel.tsx'],
      external: Object.keys(externalLibs),
      output: {
        dir: '../better_label_printer/static',
        entryFileNames: '[name].js',
        assetFileNames: 'assets/[name].[ext]',
        globals: externalLibs,
      },
    },
  },
  optimizeDeps: {
    exclude: Object.keys(externalLibs),
  },
});
