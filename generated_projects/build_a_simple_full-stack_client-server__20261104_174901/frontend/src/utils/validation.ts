export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

const TIME_REGEX = /^([01]\d|2[0-3]):[0-5]\d$/;

export function validateName(name: string): ValidationResult {
  if (!name || name.trim().length === 0) {
    return {
      isValid: false,
      error: "Name must not be empty.",
    };
  }
  return { isValid: true };
}

export function validateTime(time: string): ValidationResult {
  if (!time || time.trim().length === 0) {
    return {
      isValid: false,
      error: "Time must not be empty.",
    };
  }

  if (!TIME_REGEX.test(time)) {
    return {
      isValid: false,
      error: "Time must be in valid 24-hour HH:mm format (e.g., 14:30).",
    };
  }

  return { isValid: true };
}