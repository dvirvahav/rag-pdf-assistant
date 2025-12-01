import React from 'react';
import { useKeycloak } from '@react-keycloak/web';

export const UserProfile: React.FC = () => {
  const { keycloak } = useKeycloak();

  const handleLogout = () => {
    keycloak.logout({ redirectUri: window.location.origin });
  };

  if (!keycloak.authenticated) {
    return null;
  }

  const userInfo = keycloak.tokenParsed;
  const displayName = userInfo?.name || userInfo?.preferred_username || 'User';
  const email = userInfo?.email;

  return (
    <div className="flex items-center gap-3">
      {/* User Info */}
      <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg">
        <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
          <span className="text-white text-sm font-semibold">
            {displayName.charAt(0).toUpperCase()}
          </span>
        </div>
        <div className="hidden sm:block">
          <p className="text-sm font-medium text-gray-800">{displayName}</p>
          {email && (
            <p className="text-xs text-gray-500">{email}</p>
          )}
        </div>
      </div>

      {/* Logout Button */}
      <button
        onClick={handleLogout}
        className="flex items-center gap-2 px-3 py-2 bg-red-50 hover:bg-red-100 text-red-600 rounded-lg transition text-sm font-medium"
        title="Logout"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
        <span className="hidden sm:inline">Logout</span>
      </button>
    </div>
  );
};
