import { WEBUI_API_BASE_URL } from '$lib/constants';

/**
 * Get the query count for the current user
 * @param token The authentication token
 * @returns The user's query count
 */
export const getUserQueryCount = async (token: string) => {
  let error = null;

  const res = await fetch(`${WEBUI_API_BASE_URL}/user_stats/`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    }
  })
    .then(async (res) => {
      if (!res.ok) throw await res.json();
      return res.json();
    })
    .catch((err) => {
      console.log(err);
      error = err.detail;
      return null;
    });

  if (error) {
    throw error;
  }

  return res;
};

/**
 * Increment the query count for the current user
 * @param token The authentication token
 * @returns The updated user stats
 */
export const incrementUserQueryCount = async (token: string) => {
  let error = null;

  const res = await fetch(`${WEBUI_API_BASE_URL}/user_stats/increment`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    }
  })
    .then(async (res) => {
      if (!res.ok) throw await res.json();
      return res.json();
    })
    .catch((err) => {
      console.log(err);
      error = err.detail;
      return null;
    });

  if (error) {
    throw error;
  }

  return res;
};
