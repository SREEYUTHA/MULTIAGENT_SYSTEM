import React from 'react';

interface ErrorMessageProps {
  message: string;
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({ message }) => {
  return (
    <div
      role="alert"
      aria-live="assertive"
      style={{
        color: '#d32f2f',
        backgroundColor: '#ffebee',
        border: '1px solid #f5c6cb',
        borderRadius: '4px',
        padding: '12px 16px',
        marginTop: '16px',
        fontSize: '14px',
        lineHeight: '1.5',
      }}
    >
      <strong>Error:</strong> {message}
    </div>
  );
};

export default ErrorMessage;