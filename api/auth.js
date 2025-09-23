// Mock Authentication API for Vercel Functions
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
  if (req.method === 'POST' && req.url === '/api/auth/login') {
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
  
  // Mock health check
  if (req.method === 'GET' && req.url === '/api/health') {
    res.status(200).json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      service: 'Engineering Log Intelligence API',
      version: '1.0.0'
    });
    return;
  }
  
  // Mock analytics endpoint
  if (req.method === 'GET' && req.url === '/api/analytics') {
    res.status(200).json({
      totalLogs: 125000,
      errorRate: 2.3,
      avgResponseTime: 145,
      activeUsers: 47,
      systemHealth: 'excellent',
      recentAlerts: [
        { id: 1, message: 'High error rate detected', severity: 'warning', timestamp: new Date().toISOString() },
        { id: 2, message: 'Database connection restored', severity: 'info', timestamp: new Date().toISOString() }
      ]
    });
    return;
  }
  
  // Default response
  res.status(404).json({
    success: false,
    message: 'Endpoint not found',
    availableEndpoints: ['/api/auth/login', '/api/health', '/api/analytics']
  });
}
