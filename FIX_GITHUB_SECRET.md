# Fix GitHub Actions DATABASE_URL Secret

**Issue**: ML Analysis workflow failing with `invalid dsn: missing "=" after "***"`  
**Cause**: DATABASE_URL secret may have formatting issues or extra characters

---

## ✅ **How to Fix (2 minutes)**

### Step 1: Go to GitHub Secrets
1. Go to: **https://github.com/jp3tty/engineering-log-intelligence/settings/secrets/actions**
2. Find `DATABASE_URL` in the list
3. Click **"Update"** or the pencil icon

### Step 2: Update the Secret Value

**Copy this EXACT string** (no extra spaces, quotes, or line breaks):

```
postgresql://postgres:aeEtrFlmEjQZfcoFMQnjnCGcHWZGgpOq@switchyard.proxy.rlwy.net:51941/railway
```

**Important:**
- ❌ Do NOT add quotes around it
- ❌ Do NOT add extra line breaks
- ❌ Do NOT add spaces at the beginning or end
- ✅ Just paste the raw connection string as-is

### Step 3: Save
Click **"Update secret"**

---

## 🧪 **Test the Fix**

After updating:

1. Go to: **https://github.com/jp3tty/engineering-log-intelligence/actions**
2. Click **"ML Batch Analysis"** workflow
3. Click **"Run workflow"** → **"Run workflow"**
4. Wait 2-3 minutes
5. Should show ✅ Success

---

## 🔍 **Common Issues**

### Issue 1: Extra Quotes
**Wrong:**
```
"postgresql://postgres:aeEtrFlmEjQZfcoFMQnjnCGcHWZGgpOq@switchyard.proxy.rlwy.net:51941/railway"
```

**Correct:**
```
postgresql://postgres:aeEtrFlmEjQZfcoFMQnjnCGcHWZGgpOq@switchyard.proxy.rlwy.net:51941/railway
```

### Issue 2: Line Breaks
If you copied from a file, make sure there are no hidden line breaks (`\n` or `\r\n`)

### Issue 3: Spaces
Make sure there are no spaces before or after the URL

---

## 📝 **What Happened**

When we updated the DATABASE_URL earlier, one of these might have happened:
- Extra quotes were accidentally added
- A line break was included
- Copy/paste added invisible characters

GitHub Secrets should contain the **raw string** without any formatting.

---

## ✅ **Verification**

After fixing, your workflows should work:
- ✅ **Daily Log Generation** (5,000 logs/day at 8 AM PDT)
- ✅ **ML Batch Analysis** (every 6 hours)
- ✅ **Daily Cleanup** (7 PM PDT)

All three workflows use the same `DATABASE_URL` secret.

---

**Quick Link**: https://github.com/jp3tty/engineering-log-intelligence/settings/secrets/actions


