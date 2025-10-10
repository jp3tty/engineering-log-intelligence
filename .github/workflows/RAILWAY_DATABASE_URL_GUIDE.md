# How to Get Your Railway DATABASE_URL

## Quick Steps

1. **Go to Railway Dashboard**
   - Visit: https://railway.app/
   - Click on your project

2. **Select PostgreSQL Service**
   - Click on your PostgreSQL database service

3. **Navigate to Variables Tab**
   - Click on the **Variables** tab
   - Look for `DATABASE_URL` in the list

4. **Copy the Connection String**
   - Click the **copy icon** next to `DATABASE_URL`
   - It will look something like:
     ```
     postgresql://postgres:password@server.railway.app:5432/railway
     ```

5. **Add to GitHub Secrets**
   - Go to your GitHub repo → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `DATABASE_URL`
   - Value: Paste the copied connection string
   - Click "Add secret"

## ✅ Verification

To verify your DATABASE_URL is correct:

**Test locally:**
```bash
cd engineering_log_intelligence
source venv/bin/activate
export DATABASE_URL="your-connection-string"
python populate_database.py 10
```

If you see:
```
✅ Generated 10 log entries
✅ Connected successfully
✅ All logs inserted successfully
```

Then your DATABASE_URL is working correctly!

## 🔒 Security Notes

- **Never commit DATABASE_URL to git**
- Keep it in GitHub Secrets only
- Don't share it publicly
- Rotate credentials if exposed

## Troubleshooting

### Can't find DATABASE_URL in Railway?
- Make sure you're in the correct project
- Look in the PostgreSQL service, not the main service
- Try the **Connect** tab instead

### Connection string doesn't work?
- Ensure it starts with `postgresql://`
- Check for extra spaces or line breaks
- Verify the database is running in Railway

### Still having issues?
- Check Railway service status
- Try reconnecting to the database in Railway
- Contact Railway support if database is down

