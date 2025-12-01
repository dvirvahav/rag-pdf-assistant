import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import { App } from './App';
import reportWebVitals from './reportWebVitals';
import { ReactKeycloakProvider } from '@react-keycloak/web';
import keycloak from './auth/keycloakConfig';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

// Keycloak initialization options
const keycloakInitOptions = {
  onLoad: 'login-required' as const, // Redirect to login if not authenticated
  checkLoginIframe: false, // Disable iframe check for simpler setup
  pkceMethod: 'S256' as const, // Use PKCE for security
};

// Loading component while Keycloak initializes
const LoadingComponent = (
  <div style={{
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh',
    fontSize: '1.5rem'
  }}>
    Loading authentication...
  </div>
);

root.render(
  <React.StrictMode>
    <ReactKeycloakProvider
      authClient={keycloak}
      initOptions={keycloakInitOptions}
      LoadingComponent={LoadingComponent}
      onEvent={(event, error) => {
        console.log('Keycloak event:', event, error);
      }}
      onTokens={(tokens) => {
        console.log('Keycloak tokens updated:', {
          token: tokens.token ? 'present' : 'missing',
          refreshToken: tokens.refreshToken ? 'present' : 'missing',
        });
      }}
    >
      <App />
    </ReactKeycloakProvider>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
