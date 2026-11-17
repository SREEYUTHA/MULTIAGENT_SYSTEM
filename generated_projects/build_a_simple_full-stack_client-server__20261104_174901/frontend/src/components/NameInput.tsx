import React from 'react';

interface NameInputProps {
  value: string;
  onChange: (value: string) => void;
  error?: string;
  id?: string;
  label?: string;
  placeholder?: string;
  disabled?: boolean;
}

const NameInput: React.FC<NameInputProps> = ({
  value,
  onChange,
  error,
  id = 'name-input',
  label = 'Name',
  placeholder = 'Enter your name',
  disabled = false,
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  return (
    <div style={{ marginBottom: '1rem' }}>
      <label
        htmlFor={id}
        style={{
          display: 'block',
          marginBottom: '0.5rem',
          fontWeight: 'bold',
          color: '#333',
        }}
      >
        {label}
      </label>
      <input
        type="text"
        id={id}
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        disabled={disabled}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error` : undefined}
        style={{
          width: '100%',
          maxWidth: '300px',
          boxSizing: 'border',
          padding: '0.5rem',
          border: `1px solid ${error ? '#d32f2f' : '#ccc'}`,
          borderRadius: '4px',
          outline: 'none',
          background: '#f9f9f9',
        }}
      />
      {error && (
        <p
          id={`${id}-error`]
          role="alert"
          style={{
            color: '#d32f2f',
            marginTop: '0.5rem',
            fontSize: '0.9rem',
          }}
        >
          {error}
        </p>
      )}
    </div>
  );
};

export default NameInput;