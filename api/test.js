module.exports = (req, res) => {
  res.status(200).json({
    message: 'Hello from Vercel Functions!',
    timestamp: new Date().toISOString(),
    status: 'success',
    method: req.method
  });
};
