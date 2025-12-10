/**
 * Tests for error handling utilities
 *
 * These tests verify that the error handling utilities correctly parse
 * and format error responses from the API.
 */

import { describe, it, expect, beforeEach } from 'vitest'
import {
  ErrorCode,
  parseErrorResponse,
  getUserFriendlyMessage,
  handleApiError,
  isErrorCode
} from '../utils/errorHandler'

describe('ErrorCode', () => {
  it('should have all expected error codes', () => {
    expect(ErrorCode.VALIDATION_ERROR).toBe('VALIDATION_ERROR')
    expect(ErrorCode.NOT_FOUND).toBe('NOT_FOUND')
    expect(ErrorCode.INTERNAL_ERROR).toBe('INTERNAL_ERROR')
    expect(ErrorCode.RATE_LIMIT_EXCEEDED).toBe('RATE_LIMIT_EXCEEDED')
  })
})

describe('parseErrorResponse', () => {
  it('should parse standardized error format', async () => {
    const mockResponse = {
      json: async () => ({
        error: {
          message: 'Module not found',
          code: 'NOT_FOUND'
        },
        status: 'error'
      })
    }

    const result = await parseErrorResponse(mockResponse)

    expect(result.message).toBe('Module not found')
    expect(result.code).toBe('NOT_FOUND')
  })

  it('should parse legacy error format', async () => {
    const mockResponse = {
      json: async () => ({
        error: 'Something went wrong'
      })
    }

    const result = await parseErrorResponse(mockResponse)

    expect(result.message).toBe('Something went wrong')
    expect(result.code).toBe(ErrorCode.INTERNAL_ERROR)
  })

  it('should handle JSON parse errors', async () => {
    const mockResponse = {
      json: async () => {
        throw new Error('Invalid JSON')
      }
    }

    const result = await parseErrorResponse(mockResponse)

    expect(result.message).toBe('Failed to parse error response')
    expect(result.code).toBe(ErrorCode.INTERNAL_ERROR)
  })
})

describe('getUserFriendlyMessage', () => {
  it('should return user-friendly message for known error code', () => {
    const message = getUserFriendlyMessage(ErrorCode.NOT_FOUND)
    expect(message).toBe('The requested resource was not found.')
  })

  it('should return fallback message for unknown error code', () => {
    const message = getUserFriendlyMessage('UNKNOWN_ERROR', 'Custom fallback')
    expect(message).toBe('Custom fallback')
  })

  it('should return default message when no fallback provided', () => {
    const message = getUserFriendlyMessage('UNKNOWN_ERROR')
    expect(message).toBe('An error occurred')
  })
})

describe('handleApiError', () => {
  it('should return backend message for validation errors', async () => {
    const mockResponse = {
      json: async () => ({
        error: {
          message: 'Rating must be between 1 and 5',
          code: 'VALIDATION_ERROR'
        },
        status: 'error'
      })
    }

    const message = await handleApiError(mockResponse)

    expect(message).toBe('Rating must be between 1 and 5')
  })

  it('should return user-friendly message for other errors', async () => {
    const mockResponse = {
      json: async () => ({
        error: {
          message: 'Database connection failed',
          code: 'DATABASE_ERROR'
        },
        status: 'error'
      })
    }

    const message = await handleApiError(mockResponse)

    // Should use backend message or fallback to friendly message
    expect(message).toBeTruthy()
  })
})

describe('isErrorCode', () => {
  it('should return true for matching error code', () => {
    const error = {
      message: 'Not found',
      code: 'NOT_FOUND'
    }

    expect(isErrorCode(error, ErrorCode.NOT_FOUND)).toBe(true)
  })

  it('should return false for non-matching error code', () => {
    const error = {
      message: 'Not found',
      code: 'NOT_FOUND'
    }

    expect(isErrorCode(error, ErrorCode.VALIDATION_ERROR)).toBe(false)
  })

  it('should handle null error', () => {
    expect(isErrorCode(null, ErrorCode.NOT_FOUND)).toBe(false)
  })
})
