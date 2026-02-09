import html from '@html-eslint/eslint-plugin';
import parser from '@html-eslint/parser';

export default [
  {
    files: ["**/*.html"],
    plugins: {
      '@html-eslint': html
    },
    languageOptions: {
      parser: parser
    },
    rules: {
      'no-unused-vars': 'warn',
      'no-undef': 'warn'
    }
  }
];
