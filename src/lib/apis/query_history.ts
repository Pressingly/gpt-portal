import { WEBUI_API_BASE_URL } from '$lib/constants';

export interface QueryHistoryItem {
  query_id: string;
  timestamp: string;
  llm: string;
  input_prompt: string;
  input_tokens: number;
  input_cost: string;
  output_tokens: number;
  output_cost: string;
  total_cost: string;
}

export interface QueryHistoryResponse {
  items: QueryHistoryItem[];
  total_pages: number;
  total_records: number;
  current_page: number;
}

/**
 * Get the query history for the current user
 * @param token The authentication token
 * @param page The page number (1-based)
 * @param pageSize The number of items per page
 * @returns The query history response
 */
export const getQueryHistory = async (
  token: string,
  page: number = 1,
  pageSize: number = 8
): Promise<QueryHistoryResponse> => {
  let error = null;
  const url = `${WEBUI_API_BASE_URL}/query_history/?page=${page}&page_size=${pageSize}`;
  console.log('Fetching query history from:', url);

  const res = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    }
  })
    .then(async (res) => {
      console.log('Response status:', res.status);
      if (!res.ok) {
        const errorData = await res.json();
        console.error('Error response:', errorData);
        throw errorData;
      }
      return res.json();
    })
    .catch((err) => {
      console.error('Fetch error:', err);
      error = err.detail;
      return null;
    });

  if (error) {
    throw error;
  }

  return res;
}; 