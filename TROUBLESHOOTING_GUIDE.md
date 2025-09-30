# 🔧 Troubleshooting Guide - Engineering Log Intelligence System

**Last Updated:** September 29, 2025  
**Version:** 2.1.0

## 🚨 Production Access Issues

### Issue: Cannot Access Production URL
**Symptoms:**
- Getting authentication required error
- Redirected to Vercel login page
- 404 errors when accessing the application

**Solutions:**
1. **Use Public Health Check Endpoint:**
   ```
   https://engineering-log-intelligence.vercel.app/api/health_public
   ```

2. **Access via Vercel Dashboard:**
   - Go to https://vercel.com/jp3ttys-projects/engineering_log_intelligence
   - Use Vercel authentication to access the application

3. **Check Vercel Protection Settings:**
   - The application may have Vercel protection enabled
   - This requires proper authentication configuration

### Issue: API Endpoints Not Responding
**Symptoms:**
- API calls returning 404 errors
- CORS errors in browser console
- Timeout errors

**Solutions:**
1. **Check API Function Status:**
   - Verify all 12 API functions are deployed
   - Check Vercel function logs for errors

2. **Test Individual Endpoints:**
   ```bash
   # Health check
   curl https://engineering-log-intelligence.vercel.app/api/health_public
   
   # Authentication
   curl -X POST https://engineering-log-intelligence.vercel.app/api/auth/login \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "password123"}'
   ```

3. **Check Environment Variables:**
   - Ensure all 25+ environment variables are configured
   - Verify database connection strings are correct

## 🐛 Known Issues & Workarounds

### Issue: Incident Response Features (Day 24 Test Results)
**Status:** 66.7% success rate - Some features need refinement

**Failing Tests:**
- **Incident Creation**: Validation errors in incident creation process
- **Escalation Evaluation**: Limited escalation action execution
- **Incident from Alert**: Escalation issues when creating incidents from alerts

**Workarounds:**
1. **Use Alert Management**: Focus on alert creation and management
2. **Manual Incident Creation**: Create incidents manually through the API
3. **Monitor Test Results**: Check test results regularly for improvements

**Test the System:**
```bash
# Run incident response tests
python test_day24_incident_response.py

# Check test results
cat day24_standalone_test_results.json
```

### Issue: Frontend Loading Problems
**Symptoms:**
- Blue-purple loading screen that doesn't disappear
- JavaScript errors in browser console
- Charts not displaying

**Solutions:**
1. **Wait for Initialization:**
   - The app may take 10-30 seconds to fully initialize
   - Check browser console for initialization messages

2. **Refresh the Page:**
   - Hard refresh (Ctrl+F5 or Cmd+Shift+R)
   - Clear browser cache and cookies

3. **Check API Connection:**
   - Ensure backend services are running
   - Verify API endpoints are accessible

4. **Use Mock Data:**
   - The frontend will show mock data if API is unavailable
   - This allows you to see the interface even without backend

### Issue: Chart Display Problems
**Symptoms:**
- Charts not rendering
- Empty chart containers
- JavaScript errors related to Chart.js

**Solutions:**
1. **Check Chart.js Integration:**
   - Verify Chart.js is properly loaded
   - Check for JavaScript errors in console

2. **Use Refresh Button:**
   - Click the "Refresh" button to reload chart data
   - This triggers API calls to fetch new data

3. **Verify Data Format:**
   - Check that API is returning data in correct format
   - Look for data structure issues in browser console

## 🔧 Development Setup Issues

### Issue: Frontend Development Server Not Starting
**Symptoms:**
- `npm run dev` command fails
- Port 3001 already in use
- Module not found errors

**Solutions:**
1. **Check Node.js Version:**
   ```bash
   node --version  # Should be 18+
   npm --version   # Should be 8+
   ```

2. **Install Dependencies:**
   ```bash
   cd engineering_log_intelligence/frontend
   npm install
   ```

3. **Clear Cache:**
   ```bash
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Use Different Port:**
   ```bash
   npm run dev -- --port 3002
   ```

### Issue: Backend API Not Responding
**Symptoms:**
- API calls timing out
- Database connection errors
- Environment variable issues

**Solutions:**
1. **Check Environment Variables:**
   ```bash
   # Check if .env file exists
   ls -la .env*
   
   # Verify environment variables
   cat .env.development
   ```

2. **Test Database Connections:**
   ```bash
   python test_external_services.py
   ```

3. **Start Development Services:**
   ```bash
   # Start local services
   docker-compose -f docker-compose.dev.yml up -d
   
   # Start Vercel development server
   vercel dev
   ```

### Issue: Data Simulation Not Working
**Symptoms:**
- Log generators not producing data
- Performance issues with data generation
- Memory errors

**Solutions:**
1. **Check System Resources:**
   - Ensure sufficient RAM (8GB+ recommended)
   - Close other applications to free up memory

2. **Reduce Data Volume:**
   ```python
   # In simulator.py, reduce batch sizes
   batch_size = 1000  # Instead of 10000
   max_logs = 10000   # Instead of 100000
   ```

3. **Test Individual Generators:**
   ```bash
   # Test SPLUNK generator
   python -c "from data_simulation.splunk_generator import SPLUNKGenerator; gen = SPLUNKGenerator(); print(gen.generate_log())"
   ```

## 📊 Performance Issues

### Issue: Slow API Response Times
**Symptoms:**
- API calls taking >5 seconds
- Timeout errors
- High memory usage

**Solutions:**
1. **Check Database Performance:**
   - Verify database connections are optimized
   - Check for slow queries

2. **Enable Caching:**
   - Use Redis for caching frequently accessed data
   - Implement query result caching

3. **Optimize Queries:**
   - Add database indexes
   - Use pagination for large result sets

### Issue: High Memory Usage
**Symptoms:**
- System running out of memory
- Slow performance
- Application crashes

**Solutions:**
1. **Reduce Batch Sizes:**
   ```python
   # In data simulation
   batch_size = 1000  # Reduce from 10000
   ```

2. **Implement Streaming:**
   - Process data in smaller chunks
   - Use generators instead of lists

3. **Monitor Memory Usage:**
   ```bash
   # Check memory usage
   htop
   # or
   ps aux --sort=-%mem | head
   ```

## 🔍 Debugging Tools

### Browser Developer Tools
1. **Open Developer Console:**
   - Press F12 or right-click → Inspect
   - Check Console tab for JavaScript errors
   - Check Network tab for API call failures

2. **Check Network Requests:**
   - Look for failed API calls (red entries)
   - Check response status codes
   - Verify request/response data

### API Testing
1. **Test Individual Endpoints:**
   ```bash
   # Health check
   curl -v https://engineering-log-intelligence.vercel.app/api/health_public
   
   # Authentication
   curl -X POST https://engineering-log-intelligence.vercel.app/api/auth/login \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "password123"}'
   ```

2. **Check Vercel Logs:**
   ```bash
   vercel logs
   vercel logs --follow
   ```

### Database Testing
1. **Test Database Connections:**
   ```bash
   python test_external_services.py
   ```

2. **Check Database Health:**
   ```bash
   python -c "from src.api.health import check_database_health; print(check_database_health())"
   ```

## 📞 Getting Help

### Self-Service Resources
1. **Check Documentation:**
   - README.md - Main project overview
   - PROJECT_STATUS.md - Current status and achievements
   - PROJECT_EXPLANATION.md - Detailed technical explanation

2. **Review Test Results:**
   - Check test output files for specific error messages
   - Look for patterns in failing tests

3. **Check Logs:**
   - Vercel function logs
   - Browser console logs
   - Application logs

### Common Error Messages

**"Module not found"**
- Solution: Run `npm install` in the frontend directory

**"Database connection failed"**
- Solution: Check environment variables and database credentials

**"CORS error"**
- Solution: Verify CORS headers in vercel.json

**"Authentication required"**
- Solution: Use public health check endpoint or Vercel authentication

**"Function timeout"**
- Solution: Check function complexity and optimize queries

## 🎯 Quick Fixes

### Reset Everything
```bash
# Stop all services
docker-compose -f docker-compose.dev.yml down
vercel dev --stop

# Clear caches
npm cache clean --force
rm -rf frontend/node_modules frontend/package-lock.json

# Reinstall and restart
cd frontend && npm install
cd .. && vercel dev
```

### Check System Status
```bash
# Check all components
python test_simple_api.py
python test_external_services.py
python test_day24_incident_response.py

# Check production
curl https://engineering-log-intelligence.vercel.app/api/health_public
```

---

**Remember:** This is a complex system with many moving parts. Most issues can be resolved by checking the basics: environment variables, database connections, and API endpoints. When in doubt, start with the health check endpoint and work your way up through the system layers.
