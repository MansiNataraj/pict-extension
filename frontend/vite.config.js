import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// base './' so built asset paths work inside chrome-extension:// pages.
export default defineConfig({
  base: './',
  plugins: [react()],
  server: { port: 5173, host: true },
  build: { outDir: 'dist', emptyOutDir: true }
});
