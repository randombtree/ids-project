module.exports = {
	'root': true,
	parser: 'babel-eslint',

	'env': {
		'browser': true,
		'es6': true,
	},
	'extends': [
		'eslint:recommended',
		'plugin:react/recommended'
	],
	'globals': {
		'Atomics': 'readonly',
		'SharedArrayBuffer': 'readonly'
	},
	'parserOptions': {
		'ecmaFeatures': {
			'jsx': true
		},
		'ecmaVersion': 2018,
		'sourceType': 'module'

	},
	'plugins': [
		'react',
		'babel',
	],
	'settings': {
		'react': {
			'version': 'detect'
		}
	},
	'rules': {
		'linebreak-style': [
			'error',
			'unix'
		],
		'no-unused-vars': [
			'error',
			{
				'argsIgnorePattern': '^_.*',
				'varsIgnorePattern': '^_.*',
			}
		],
	}

}
