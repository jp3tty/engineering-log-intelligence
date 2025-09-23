// Mock Logout API for Vercel Functions
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

  // Mock logout endpoint
  if (req.method === 'POST') {
    res.status(200).json({
      success: true,
      message: 'Logout successful'
    });
    return;
  }
  
  // Default response
  res.status(404).json({
    success: false,
    message: 'Endpoint not found'
  });
}
