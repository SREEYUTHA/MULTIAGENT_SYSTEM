import React from 'react';

interface SubmitButtonProps {
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
  children?: React.ReactNode;
}

const SubmitButton: React.FC<SubmitButtonProps> = ({
  onClick,
  disabled = false,
  loading = false,
  children = 'Submit',
}) => {
  const isDisabled = disabled || loading;

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={isDisabled}
      aria-busy={loading}
      style={{
        padding: '0.5rem 1rem',
        fontSize: '1rem',
        backgroundColor: isDisabled ? '#ccc' : '#007bff',
        color: '#fff',
        border: 'none',
        borderRadius: '4px',
        cursor: isDisabled ? 'not-allowed' : 'pointer',
        transition: 'background-color 0.2s ease',
      }}
    >
      {loading ? 'Loading...' : children}
    </button>
  );
};

export default SubmitButton;