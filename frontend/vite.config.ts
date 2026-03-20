import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";


export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/candidates": "http://localhost:8000",
    },
  },
});
