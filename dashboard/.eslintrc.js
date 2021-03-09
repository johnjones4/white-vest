module.exports = {
  extends: [
    'standard',
    'standard-jsx',
    'standard-react',
    'standard-with-typescript'
  ],
  rules: {
    'react/jsx-uses-react': 'off',
    'react/react-in-jsx-scope': 'off'
  },
  parserOptions: {
    project: './tsconfig.json',
    tsconfigRootDir: __dirname
  }
}
