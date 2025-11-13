// eslint.config.js
import js from "@eslint/js";
import { defineConfig } from "eslint/config";

export default defineConfig([
	{
		plugins: {
			js,
		},
		extends: ["js/recommended"],
		rules: {
			"no-unused-vars": "warn",
		},
	},
]);