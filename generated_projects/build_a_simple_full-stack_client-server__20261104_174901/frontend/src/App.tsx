import { useState, FormEvent } from 'react';

interface GreetingResponse {
  message: string;
}

interface ErrorResponse {
  error: string;
}

export default function App() {
  const [name, setName] = useState('');
  const [greeting, setGreeting] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const trimmedName = name.trim();
    if (!trimmedName) {
      setError('Please enter a name.');
      return;
    }

    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const time = `${hours}:${minutes}`;

    setIsLoading(true);
    setError('');
    setGreeting('');

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';
      const response = await fetch(
        `${apiUrl}/api/hello?name=${encodeURIComponent(trimmedName)}&time=${encodeURIComponent(time)}`
      );

      if (!response.ok) {
        let errorMessage = 'An unexpected error occurred.';
        try {
          const data: ErrorResponse = await response.json();
          if (data.error) {
            errorMessage = data.error;
          }
        } catch {
          // Ignore JSON parse errors and use default message
        }
        throw new Error(errorMessage);
      }

      const data: GreetingResponse = await response.json();
      setGreeting(data.message);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '50px auto', padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Greeting App</h1>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="name" style={{ display: 'block', marginBottom: '5px' }}>
            Name
          </label>
          <input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
            aria-label="User name"
          />
        </div>
        <button
          type="submit"
          disabled={isLoading}
          style={{ padding: '10px 20px', cursor: isLoading ? 'not-allowed' : 'pointer' }}
        >
          {isLoading ? 'Loading...' : 'Submit'}
        </button>
      </form>

      <div aria-live="polite" style={{ marginTop: '20px' }}>
        {isLoading && <p>Loading...</p>}
        {greeting && <p style={{ color: 'green' }}>{greeting}</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}
      </div>
    </div>
  );
}