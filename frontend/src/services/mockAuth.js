/**
 * Mock Authentication Service
 * =========================
 * 
 * This service provides mock authentication for development when
 * the backend API is not available.
 * 
 * For beginners: This is a fake authentication system that simulates
 * what a real backend would do, but without needing a server.
 * 
 * Author: Engineering Log Intelligence Team
 * Date: September 22, 2025
 */

// Mock user database
const mockUsers = {
  'admin': {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    role: 'admin',
    permissions: ['read_logs', 'view_dashboard', 'create_alerts', 'analyze_logs', 'export_data', 'manage_users', 'manage_system', 'configure_alerts'],
    first_name: 'Admin',
    last_name: 'User'
  },
  'analyst': {
    id: 2,
    username: 'analyst',
    email: 'analyst@example.com',
    role: 'analyst',
    permissions: ['read_logs', 'view_dashboard', 'create_alerts', 'analyze_logs', 'export_data'],
    first_name: 'Analyst',
    last_name: 'User'
  },
  'user': {
    id: 3,
    username: 'user',
    email: 'user@example.com',
    role: 'user',
    permissions: ['read_logs', 'view_dashboard', 'create_alerts'],
    first_name: 'Regular',
    last_name: 'User'
  }
}

// Mock password (in real app, this would be hashed)
const mockPasswords = {
  'admin': 'password123',
  'analyst': 'password123',
  'user': 'password123'
}

/**
 * Mock login function
 * 
 * For beginners: This simulates what happens when you try to log in.
 * It checks if the username and password are correct, and if so,
 * returns user data and tokens.
 */
export const mockLogin = async (credentials) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  const { username, password } = credentials
  
  // Check if user exists
  if (!mockUsers[username]) {
    throw new Error('Invalid username or password')
  }
  
  // Check password
  if (mockPasswords[username] !== password) {
    throw new Error('Invalid username or password')
  }
  
  // Generate mock tokens
  const accessToken = `mock_access_token_${username}_${Date.now()}`
  const refreshToken = `mock_refresh_token_${username}_${Date.now()}`
  
  // Return mock response
  return {
    user: mockUsers[username],
    tokens: {
      access_token: accessToken,
      refresh_token: refreshToken,
      expires_in: 1800 // 30 minutes
    }
  }
}

/**
 * Mock token verification
 * 
 * For beginners: This simulates checking if a token is still valid.
 * In a real app, this would verify the token with the server.
 */
export const mockVerifyToken = async (token) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500))
  
  // Check if token looks valid (starts with mock_access_token_)
  if (token && token.startsWith('mock_access_token_')) {
    return { valid: true }
  }
  
  throw new Error('Invalid token')
}

/**
 * Mock token refresh
 * 
 * For beginners: This simulates refreshing an expired token.
 * In a real app, this would get a new token from the server.
 */
export const mockRefreshToken = async (refreshToken) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500))
  
  // Check if refresh token looks valid
  if (refreshToken && refreshToken.startsWith('mock_refresh_token_')) {
    // Extract username from refresh token
    const username = refreshToken.split('_')[3]
    
    if (mockUsers[username]) {
      // Generate new tokens
      const newAccessToken = `mock_access_token_${username}_${Date.now()}`
      const newRefreshToken = `mock_refresh_token_${username}_${Date.now()}`
      
      return {
        user: mockUsers[username],
        tokens: {
          access_token: newAccessToken,
          refresh_token: newRefreshToken,
          expires_in: 1800
        }
      }
    }
  }
  
  throw new Error('Invalid refresh token')
}

/**
 * Mock logout
 * 
 * For beginners: This simulates logging out.
 * In a real app, this would tell the server to invalidate the token.
 */
export const mockLogout = async (token) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 300))
  
  // In a real app, this would invalidate the token on the server
  console.log('Mock logout for token:', token)
  
  return { success: true }
}
