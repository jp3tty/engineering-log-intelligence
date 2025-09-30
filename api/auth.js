// Simple Authentication API for Vercel Functions
export default function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // Mock login endpoint
  if (req.method === 'POST') {
    const { username, password } = req.body;
    
    // Mock authentication logic
    const validCredentials = {
      'admin': 'password123',
      'analyst': 'password123',
      'user': 'password123',
      'demo': 'password123'
    };
    
    if (validCredentials[username] && validCredentials[username] === password) {
      // Mock successful login
      const mockUser = {
        id: 1,
        username: username,
        email: `${username}@example.com`,
        role: username === 'admin' ? 'admin' : username === 'analyst' ? 'analyst' : 'user',
        permissions: username === 'admin' ? 
          ['read_logs', 'manage_users', 'configure_alerts', 'analyze_logs'] :
          username === 'analyst' ?
          ['read_logs', 'analyze_logs', 'create_alerts'] :
          ['read_logs', 'view_dashboard']
      };
      
      const mockToken = `mock_token_${username}_${Date.now()}`;
      
      res.status(200).json({
        success: true,
        user: mockUser,
        token: mockToken,
        message: 'Login successful'
      });
    } else {
      res.status(401).json({
        success: false,
        message: 'Invalid credentials'
      });
    }
    return;
  }
  
  // Default response
  res.status(404).json({
    success: false,
    message: 'Endpoint not found'
  });
};