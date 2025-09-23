// Mock Health Check API for Vercel Functions
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

  // Mock health check endpoint
  if (req.method === 'GET') {
    res.status(200).json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      service: 'Engineering Log Intelligence API',
      version: '1.0.0',
      uptime: '99.9%',
      database: 'connected',
      cache: 'active'
    });
    return;
  }
  
  // Default response
  res.status(404).json({
    success: false,
    message: 'Endpoint not found'
  });
}
