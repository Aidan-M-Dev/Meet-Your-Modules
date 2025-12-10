/**
 * Error handling utilities for Meet Your Modules frontend.
 *
 * Provides consistent error parsing and user-friendly error messages
 * for API responses.
 */

/**
 * Error codes that match backend error codes
 */
export const ErrorCode = {
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  NOT_FOUND: 'NOT_FOUND',
  BAD_REQUEST: 'BAD_REQUEST',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  RATE_LIMIT_EXCEEDED: 'RATE_LIMIT_EXCEEDED',
  NOT_IMPLEMENTED: 'NOT_IMPLEMENTED',
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  DATABASE_ERROR: 'DATABASE_ERROR',
  EXTERNAL_SERVICE_ERROR: 'EXTERNAL_SERVICE_ERROR',
}

/**
 * User-friendly error messages for common error codes
 */
const ERROR_MESSAGES = {
  [ErrorCode.VALIDATION_ERROR]: 'Please check your input and try again.',
  [ErrorCode.NOT_FOUND]: 'The requested resource was not found.',
  [ErrorCode.UNAUTHORIZED]: 'You must be logged in to perform this action.',
  [ErrorCode.FORBIDDEN]: 'You do not have permission to perform this action.',
  [ErrorCode.RATE_LIMIT_EXCEEDED]: 'Too many requests. Please slow down and try again later.',
  [ErrorCode.NOT_IMPLEMENTED]: 'This feature is coming soon!',
  [ErrorCode.INTERNAL_ERROR]: 'Something went wrong on our end. Please try again later.',
  [ErrorCode.DATABASE_ERROR]: 'Database error. Please try again later.',
  [ErrorCode.EXTERNAL_SERVICE_ERROR]: 'External service error. Please try again later.',
}

/**
 * Parse an error response from the API
 *
 * @param {Response} response - Fetch API response object
 * @returns {Promise<{message: string, code: string}>} Parsed error object
 */
export async function parseErrorResponse(response) {
  try {
    const data = await response.json()

    // New standardized format: { error: { message, code }, status: "error" }
    if (data.error && data.error.message && data.error.code) {
      return {
        message: data.error.message,
        code: data.error.code,
      }
    }

    // Legacy format: { error: "message" }
    if (data.error && typeof data.error === 'string') {
      return {
        message: data.error,
        code: ErrorCode.INTERNAL_ERROR,
      }
    }

    // Fallback for unexpected formats
    return {
      message: 'An unexpected error occurred',
      code: ErrorCode.INTERNAL_ERROR,
    }
  } catch (e) {
    // JSON parsing failed
    return {
      message: 'Failed to parse error response',
      code: ErrorCode.INTERNAL_ERROR,
    }
  }
}

/**
 * Get a user-friendly error message for an error code
 *
 * @param {string} errorCode - Error code from backend
 * @param {string} [fallbackMessage] - Optional fallback message
 * @returns {string} User-friendly error message
 */
export function getUserFriendlyMessage(errorCode, fallbackMessage = null) {
  return ERROR_MESSAGES[errorCode] || fallbackMessage || 'An error occurred'
}

/**
 * Handle an API error and return a user-friendly message
 *
 * @param {Response} response - Fetch API response object
 * @returns {Promise<string>} User-friendly error message
 *
 * @example
 * try {
 *   const response = await fetch('/api/v1/submitReview/123', { method: 'POST', ... })
 *   if (!response.ok) {
 *     const errorMessage = await handleApiError(response)
 *     alert(errorMessage)
 *     return
 *   }
 *   const data = await response.json()
 *   // Handle success
 * } catch (error) {
 *   alert('Network error. Please check your connection.')
 * }
 */
export async function handleApiError(response) {
  const error = await parseErrorResponse(response)

  // For validation errors, use the specific message from backend
  if (error.code === ErrorCode.VALIDATION_ERROR) {
    return error.message
  }

  // For other errors, prefer backend message, fallback to friendly message
  return error.message || getUserFriendlyMessage(error.code)
}

/**
 * Display an error message to the user
 *
 * @param {string} message - Error message to display
 * @param {HTMLElement} [container] - Optional container element to display error in
 *
 * @example
 * // Display in alert
 * displayError('Something went wrong')
 *
 * // Display in specific element
 * const errorContainer = document.getElementById('error-container')
 * displayError('Invalid input', errorContainer)
 */
export function displayError(message, container = null) {
  if (container) {
    // Display in specified container
    container.textContent = message
    container.style.display = 'block'
    container.classList.add('error-message')
  } else {
    // Fallback to alert
    alert(message)
  }
}

/**
 * Clear error message from a container
 *
 * @param {HTMLElement} container - Container element to clear error from
 */
export function clearError(container) {
  if (container) {
    container.textContent = ''
    container.style.display = 'none'
    container.classList.remove('error-message')
  }
}

/**
 * Check if a response is successful (status 2xx and status: "success")
 *
 * @param {Response} response - Fetch API response object
 * @returns {Promise<boolean>} True if successful
 */
export async function isSuccessfulResponse(response) {
  if (!response.ok) {
    return false
  }

  try {
    const data = await response.json()
    return data.status === 'success'
  } catch (e) {
    // If we can't parse JSON, assume success based on HTTP status
    return response.ok
  }
}

/**
 * Fetch wrapper with automatic error handling
 *
 * @param {string} url - API endpoint URL
 * @param {RequestInit} [options] - Fetch options
 * @returns {Promise<any>} Response data
 * @throws {Error} Error with user-friendly message
 *
 * @example
 * try {
 *   const data = await fetchWithErrorHandling('/api/searchModules?q=computing')
 *   console.log('Modules:', data.modules)
 * } catch (error) {
 *   alert(error.message)
 * }
 */
export async function fetchWithErrorHandling(url, options = {}) {
  try {
    const response = await fetch(url, options)

    if (!response.ok) {
      const errorMessage = await handleApiError(response)
      throw new Error(errorMessage)
    }

    const data = await response.json()
    return data
  } catch (error) {
    // Network error or parsing error
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Network error. Please check your connection.')
    }
    // Re-throw errors from handleApiError
    throw error
  }
}

/**
 * Helper to check if an error is a specific error code
 *
 * @param {Object} error - Parsed error object
 * @param {string} errorCode - Error code to check
 * @returns {boolean} True if error matches code
 */
export function isErrorCode(error, errorCode) {
  return error && error.code === errorCode
}

export default {
  ErrorCode,
  parseErrorResponse,
  getUserFriendlyMessage,
  handleApiError,
  displayError,
  clearError,
  isSuccessfulResponse,
  fetchWithErrorHandling,
  isErrorCode,
}
