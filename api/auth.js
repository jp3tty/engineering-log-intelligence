/**
 * Authentication endpoint for Vercel Functions (Node.js version)
 */

module.exports = (req, res) => {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.setHeader('Content-Type', 'application/json');

  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.status(200).json({ message: 'CORS preflight successful' });
    return;
  }

  try {
    if (req.method === 'POST') {
      // Handle login request
      let body = '';
      req.on('data', chunk => {
        body += chunk.toString();
      });
      
      req.on('end', () => {
        try {
          const data = JSON.parse(body);
          const username = data.username?.trim() || '';
          const password = data.password?.trim() || '';

          // Demo credentials for testing
          const demoUsers = {
            'admin': {
              password: 'password123',
              role: 'admin',
              permissions: ['read_logs', 'view_dashboard', 'create_alerts', 'analyze_logs', 'export_data', 'manage_users', 'manage_system', 'configure_alerts']
            },
            'analyst': {
              password: 'password123',
              role: 'analyst',
              permissions: ['read_logs', 'view_dashboard', 'create_alerts', 'analyze_logs', 'export_data']
            },
            'user': {
              password: 'password123',
              role: 'user',
              permissions: ['read_logs', 'view_dashboard', 'create_alerts']
            }
          };

          // Check credentials
          if (username in demoUsers && demoUsers[username].password === password) {
            // Generate tokens (simplified for demo)
            const timestamp = Date.now();
            const accessToken = `demo_access_token_${username}_${timestamp}`;
            const refreshToken = `demo_refresh_token_${username}_${timestamp}`;

            const userData = {
              id: 1,
              username: username,
              email: `${username}@example.com`,
              role: demoUsers[username].role,
              permissions: demoUsers[username].permissions,
              first_name: username.charAt(0).toUpperCase() + username.slice(1),
              last_name: 'User'
            };

            res.status(200).json({
              user: userData,
              tokens: {
                access_token: accessToken,
                refresh_token: refreshToken,
                expires_in: 1800
              },
              timestamp: new Date().toISOString()
            });
          } else {
            res.status(401).json({
              error: 'Invalid credentials',
              message: 'Username or password is incorrect'
            });
          }
        } catch (parseError) {
          res.status(400).json({
            error: 'Invalid JSON',
            message: 'Request body must be valid JSON'
          });
        }
      });
    } else {
      // Handle GET request - return endpoint info
      res.status(200).json({
        message: 'Authentication endpoint',
        timestamp: new Date().toISOString(),
        status: 'success',
        environment: process.env.NODE_ENV || 'development',
        available_methods: ['POST', 'GET', 'OPTIONS']
      });
    }
  } catch (error) {
    res.status(500).json({
      error: 'Internal server error',
      message: error.message,
      timestamp: new Date().toISOString()
    });
  }
};
