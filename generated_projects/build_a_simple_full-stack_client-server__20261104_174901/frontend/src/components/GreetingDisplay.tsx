import React from 'react';

interface GreetingDisplayProps {
  message: string;
}

const GreetingDisplay: React.FC<GreetingDisplayProps> = ({ message }) => {
  return (
    <div
      role="status"
      aria-live="polite"
      style={{
        marginTop: '1rem',
        padding: '1rem',
        backgroundColor: '#f0f8ff',
        border: '1px solid #b3d4fc',
        borderRadius: '4px',
        fontSize: '1.25rem',
        color: '#003366',
        textAlign: 'center',
      }}
    >
      {message}
    </div>
  );
};

export default GreetingDisplay;