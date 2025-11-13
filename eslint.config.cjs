// eslint.config.cjs
import { FlatCompat } from '@eslint/eslintrc';

const compat = new FlatCompat({
  baseConfig: {
    parserOptions: { ecmaVersion: 2020 },
    env: { browser: true, es2021: true },
    rules: {
      semi: ['error', 'always'],
      quotes: ['error', 'single'],
    },
  },
  recommendedConfig: true,
});

export default [
  compat.config,
];
