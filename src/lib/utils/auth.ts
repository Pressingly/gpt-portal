/**
 * Get the authentication token from cookies or localStorage
 * @returns The authentication token
 * @throws Error if no token is found
 */
export const getToken = async (): Promise<string> => {
  // First check localStorage
  const localToken = localStorage.getItem('token');
  if (localToken) {
    return localToken;
  }

  // Then check cookies
  const cookies = document.cookie.split(';');
  const tokenCookie = cookies.find(cookie => cookie.trim().startsWith('token='));
  if (tokenCookie) {
    return tokenCookie.split('=')[1];
  }

  throw new Error('No authentication token found');
}; 