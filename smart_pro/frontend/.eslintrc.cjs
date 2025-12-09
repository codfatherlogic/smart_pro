module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    "eslint:recommended",
    "plugin:vue/vue3-recommended",
  ],
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module",
  },
  plugins: ["vue"],
  rules: {
    "vue/multi-word-component-names": "off",
    "vue/no-v-html": "off",
    "no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
  },
  globals: {
    frappe: "readonly",
    __: "readonly",
  },
}
