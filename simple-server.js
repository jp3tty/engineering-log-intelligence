const http = require('http');
const url = require('url');

const server = http.createServer((req, res) => {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.setHeader('Content-Type', 'application/json');

  const parsedUrl = url.parse(req.url, true);
  const path = parsedUrl.pathname;

  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end(JSON.stringify({ message: 'CORS preflight successful' }));
    return;
  }

  // Handle different endpoints
  if (path === '/api/auth' && req.method === 'GET') {
    res.writeHead(200);
    res.end(JSON.stringify({
      message: 'Authentication endpoint',
      timestamp: new Date().toISOString(),
      status: 'success',
      environment: 'development',
      available_methods: ['POST', 'GET', 'OPTIONS']
    }));
    return;
  }

  // Handle login endpoint
  if (path === '/api/auth/login' && req.method === 'POST') {
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

          res.writeHead(200);
          res.end(JSON.stringify({
            user: userData,
            tokens: {
              access_token: accessToken,
              refresh_token: refreshToken,
              expires_in: 1800
            },
            timestamp: new Date().toISOString()
          }));
        } else {
          res.writeHead(401);
          res.end(JSON.stringify({
            error: 'Invalid credentials',
            message: 'Username or password is incorrect'
          }));
        }
      } catch (parseError) {
        res.writeHead(400);
        res.end(JSON.stringify({
          error: 'Invalid JSON',
          message: 'Request body must be valid JSON'
        }));
      }
    });
    return;
  }

  // Handle logout endpoint
  if (path === '/api/auth/logout' && req.method === 'POST') {
    res.writeHead(200);
    res.end(JSON.stringify({
      message: 'Logged out successfully',
      timestamp: new Date().toISOString()
    }));
    return;
  }

  // Handle token verification endpoint
  if (path === '/api/auth/verify' && req.method === 'GET') {
    const authHeader = req.headers.authorization;
    if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.substring(7);
      // Simple token validation for demo
      if (token.startsWith('demo_access_token_')) {
        res.writeHead(200);
        res.end(JSON.stringify({
          valid: true,
          message: 'Token is valid',
          timestamp: new Date().toISOString()
        }));
        return;
      }
    }
    res.writeHead(401);
    res.end(JSON.stringify({
      error: 'Invalid token',
      message: 'Token is invalid or expired'
    }));
    return;
  }

  // Handle token refresh endpoint
  if (path === '/api/auth/refresh' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
    });
    
    req.on('end', () => {
      try {
        const data = JSON.parse(body);
        const refreshToken = data.refresh_token;
        
        if (refreshToken && refreshToken.startsWith('demo_refresh_token_')) {
          // Extract username from refresh token
          const parts = refreshToken.split('_');
          const username = parts[3];
          
          // Generate new tokens
          const timestamp = Date.now();
          const newAccessToken = `demo_access_token_${username}_${timestamp}`;
          const newRefreshToken = `demo_refresh_token_${username}_${timestamp}`;

          res.writeHead(200);
          res.end(JSON.stringify({
            tokens: {
              access_token: newAccessToken,
              refresh_token: newRefreshToken,
              expires_in: 1800
            },
            timestamp: new Date().toISOString()
          }));
        } else {
          res.writeHead(401);
          res.end(JSON.stringify({
            error: 'Invalid refresh token',
            message: 'Refresh token is invalid or expired'
          }));
        }
      } catch (parseError) {
        res.writeHead(400);
        res.end(JSON.stringify({
          error: 'Invalid JSON',
          message: 'Request body must be valid JSON'
        }));
      }
    });
    return;
  }


  if (path === '/api/test') {
    res.writeHead(200);
    res.end(JSON.stringify({
      message: "Hello from Simple Server!",
      timestamp: new Date().toISOString(),
      method: req.method,
      url: req.url
    }));
    return;
  }

  // Default 404
  res.writeHead(404);
  res.end(JSON.stringify({
    error: 'Not Found',
    message: 'The requested endpoint was not found'
  }));
});

const PORT = 3000;
server.listen(PORT, () => {
  console.log(`🚀 Simple server running on http://localhost:${PORT}`);
  console.log(`📡 Available endpoints:`);
  console.log(`   GET  /api/test`);
  console.log(`   GET  /api/auth`);
  console.log(`   POST /api/auth`);
});
