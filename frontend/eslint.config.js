import js from '@eslint/js'
import prettier from 'eslint-config-prettier'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import globals from 'globals'
import tseslint from 'typescript-eslint'

export default tseslint.config(
  { ignores: ['dist', 'coverage'] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  // v7 keeps the legacy shape at configs['recommended-latest']; the flat config
  // lives one level down.
  reactHooks.configs.flat['recommended-latest'],
  reactRefresh.configs.vite,
  prettier,
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2023,
      globals: globals.browser,
    },
    rules: {
      // `any` is banned by the project rules; `unknown` plus an explicit
      // narrowing is the accepted alternative.
      '@typescript-eslint/no-explicit-any': 'error',
    },
  },
)
