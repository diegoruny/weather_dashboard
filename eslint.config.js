import js from "@eslint/js";
import { defineConfig } from "eslint/config";

export default defineConfig([
  {
    plugins: {
      js,
    },
    extends: ["js/recommended"],
    languageOptions: {
      env: {
        browser: true,   // adds document, window, console, fetch, etc.
        es2021: true,    // modern JS globals
      },
    },
    rules: {
      "no-unused-vars": "warn",
    },
  },
]);