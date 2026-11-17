import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
// @ts-ignore Vite processes this CSS side-effect import.
import './index.css';

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('Root element with id "root" not found in the document.');
}

const root = ReactDOM.createRoot(rootElement);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);