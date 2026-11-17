const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

export interface HelloResponse {
  message: string;
}

export interface HelloError {
  error: string;
}

export async function fetchHello(name: string, time: string): Promise<HelloResponse> {
  const url = new URL(`${API_URL}/api/hello`);
  url.searchParams.set('name', name);
  url.searchParams.set('time', time);

  const response = await fetch(url.toString());

  if (!response.ok) {
    let errorMessage = 'An unexpected error occurred.';
    try {
      const data: HelloError = await response.json();
      if (data.error) {
        errorMessage = data.error;
      }
    } catch {
      // Ignore JSON parse errors and use default message
    }
    throw new Error(errorMessage);
  }

  const data: HelloResponse = await response.json();
  return data;
}