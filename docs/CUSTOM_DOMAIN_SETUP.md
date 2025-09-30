# Custom Domain Setup Guide

## 🎯 **What We're Doing**

We're going to set up a custom domain for our Engineering Log Intelligence System to make it look more professional and memorable.

## 🌐 **Current vs. Future URLs**

**Current URL (Vercel default):**
```
https://engineering-log-intelligence.vercel.app
```

**Future URL (with custom domain):**
```
https://logintelligence.com
```
or
```
https://engineeringlogs.ai
```

## 📚 **Learning: What is a Custom Domain?**

### Domain Basics
- **Domain**: A human-readable address for websites (like `google.com`)
- **Subdomain**: Part before the main domain (like `www.google.com`)
- **TLD**: Top-level domain (like `.com`, `.ai`, `.io`)
- **DNS**: Domain Name System - translates domains to IP addresses

### Why Use a Custom Domain?
1. **Professional Appearance**: Looks more credible than Vercel URLs
2. **Branding**: Easier to remember and share
3. **SEO**: Better for search engine optimization
4. **Trust**: Users trust custom domains more
5. **Marketing**: Easier to promote and advertise

## 🛒 **Step 1: Choose and Purchase a Domain**

### Option A: Buy Domain Through Vercel (Recommended)
```bash
# This will open Vercel's domain purchase interface
vercel domains buy logintelligence.com
```

### Option B: Buy Domain from External Provider
Popular domain registrars:
- **Namecheap**: Good prices, easy to use
- **GoDaddy**: Popular but more expensive
- **Google Domains**: Simple and reliable
- **Cloudflare**: Good security features

### Domain Name Suggestions
- `logintelligence.com`
- `engineeringlogs.ai`
- `loganalyzer.io`
- `smartlogs.dev`
- `loginsights.tech`

## 🔧 **Step 2: Configure Domain in Vercel**

### If You Bought Through Vercel
The domain will be automatically configured. Skip to Step 3.

### If You Bought Externally
1. **Add Domain to Vercel:**
   ```bash
   vercel domains add yourdomain.com engineering_log_intelligence
   ```

2. **Get DNS Configuration:**
   ```bash
   vercel domains inspect yourdomain.com
   ```

3. **Configure DNS Records:**
   - Go to your domain registrar's DNS settings
   - Add the DNS records provided by Vercel
   - Wait for DNS propagation (can take up to 24 hours)

## ⚙️ **Step 3: Configure SSL Certificate**

Vercel automatically provides SSL certificates, but we need to ensure they're configured:

### Check SSL Status
```bash
vercel domains inspect yourdomain.com
```

### SSL Configuration
- Vercel automatically handles SSL certificates
- Certificates are free and auto-renewed
- HTTPS is enabled by default
- No additional configuration needed

## 🧪 **Step 4: Test the Domain**

### Test Commands
```bash
# Test if domain is working
curl -I https://yourdomain.com

# Test if SSL is working
curl -I https://yourdomain.com --insecure
```

### Browser Testing
1. Visit your custom domain
2. Check that it shows our Vue.js application
3. Verify the SSL certificate is valid
4. Test all functionality

## 📋 **Step 5: Update Configuration**

### Update Vercel Configuration
We might need to update our `vercel.json` to handle the custom domain:

```json
{
  "version": 2,
  "builds": [
    // ... existing builds
  ],
  "rewrites": [
    // ... existing rewrites
  ],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Access-Control-Allow-Origin",
          "value": "https://yourdomain.com"
        }
      ]
    }
  ]
}
```

### Update Environment Variables
Update CORS origins to include your custom domain:
```bash
vercel env add CORS_ORIGINS production
# Enter: https://yourdomain.com,https://engineeringlogintelligence.vercel.app
```

## 🚨 **Troubleshooting**

### Common Issues

#### Domain Not Working
1. **Check DNS Propagation:**
   ```bash
   nslookup yourdomain.com
   ```

2. **Wait for Propagation:**
   - DNS changes can take 24-48 hours
   - Use online tools to check propagation status

3. **Check Vercel Configuration:**
   ```bash
   vercel domains inspect yourdomain.com
   ```

#### SSL Certificate Issues
1. **Check Certificate Status:**
   ```bash
   vercel domains inspect yourdomain.com
   ```

2. **Force SSL Renewal:**
   - Vercel handles this automatically
   - Contact support if issues persist

#### CORS Issues
1. **Update CORS Origins:**
   - Add your custom domain to CORS_ORIGINS
   - Update vercel.json headers

2. **Test API Endpoints:**
   ```bash
   curl -H "Origin: https://yourdomain.com" https://yourdomain.com/api/health_public
   ```

## 💰 **Cost Considerations**

### Domain Costs
- **.com domains**: ~$10-15/year
- **.ai domains**: ~$50-100/year
- **.io domains**: ~$30-50/year
- **.dev domains**: ~$20-30/year

### Vercel Costs
- **Domain management**: Free
- **SSL certificates**: Free
- **DNS hosting**: Free
- **No additional Vercel costs**

## ✅ **Success Criteria**

After completing setup:
- [ ] Custom domain loads our application
- [ ] SSL certificate is valid and working
- [ ] All API endpoints work with custom domain
- [ ] CORS is properly configured
- [ ] Application functions normally

## 🎉 **Next Steps**

Once custom domain is working:
1. Update all documentation with new URL
2. Test all functionality thoroughly
3. Set up monitoring for the custom domain
4. Consider setting up redirects from old URL
5. Update any hardcoded URLs in the code

## 📚 **Learning Summary**

### What You've Learned
1. **Domain Management**: How domains work and how to configure them
2. **DNS Configuration**: How to set up DNS records
3. **SSL Certificates**: How HTTPS works and how to configure it
4. **Vercel Integration**: How to connect custom domains to Vercel
5. **Production Deployment**: How to make applications publicly accessible

### Skills Gained
- Domain registration and management
- DNS configuration
- SSL certificate understanding
- Production deployment best practices
- Troubleshooting domain issues

This knowledge is valuable for any web development project and shows understanding of production deployment concepts!
