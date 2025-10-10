# Daily Log Generation Setup Guide

## Overview

This GitHub Actions workflow automatically generates new log entries in your Railway PostgreSQL database every day at 2 AM UTC.

## Setup Instructions

### 1. Add GitHub Secret

You need to add your Railway database URL as a GitHub secret:

1. **Get your Railway Database URL:**
   - Go to your Railway project dashboard
   - Navigate to your PostgreSQL service
   - Copy the `DATABASE_URL` connection string (should start with `postgresql://`)

2. **Add to GitHub Secrets:**
   - Go to your GitHub repository
   - Click **Settings** → **Secrets and variables** → **Actions**
   - Click **New repository secret**
   - Name: `DATABASE_URL`
   - Value: Paste your Railway PostgreSQL connection string
   - Click **Add secret**

### 2. Verify the Setup

The workflow is now configured to run automatically, but you can test it manually:

1. Go to your GitHub repository
2. Click **Actions** tab
3. Select **Daily Log Generation** workflow
4. Click **Run workflow** dropdown
5. (Optional) Change the number of logs to generate
6. Click **Run workflow** button

### 3. Monitor Execution

After the workflow runs:
- Check the **Actions** tab for execution status
- View detailed logs by clicking on the workflow run
- Verify new logs in your Railway database

## Configuration

### Schedule

The workflow runs daily at **2 AM UTC**, which is:
- **9 PM EST** (previous day)
- **6 PM PST** (previous day)

To change the schedule, edit `.github/workflows/daily-log-generation.yml`:
```yaml
schedule:
  - cron: '0 2 * * *'  # Format: minute hour day month weekday
```

**Examples:**
- `0 12 * * *` - Run at noon UTC every day
- `0 0 * * 1` - Run at midnight UTC every Monday
- `0 */6 * * *` - Run every 6 hours

### Log Count

By default, the workflow generates **1000 logs per day**. To change:

**Option 1: Update the default in the workflow file**
```yaml
default: '1000'  # Change this number
```

**Option 2: Specify when manually running**
- Use the workflow dispatch input field in GitHub UI

### Disable Automatic Generation

To temporarily disable automatic daily generation:

**Option 1: Disable the workflow**
- Go to Actions → Daily Log Generation → ⋯ menu → Disable workflow

**Option 2: Comment out the schedule**
Edit the workflow file:
```yaml
# schedule:
#   - cron: '0 2 * * *'
```

## Troubleshooting

### Workflow fails with "DATABASE_URL not found"
- Verify the GitHub secret is named exactly `DATABASE_URL`
- Check that the secret value is a valid PostgreSQL connection string

### Workflow completes but no logs appear
- Check the workflow logs for error messages
- Verify your Railway database is accessible
- Test the script locally: `python populate_database.py 100`

### Want to generate logs immediately?
Use the manual trigger:
1. Actions tab → Daily Log Generation
2. Run workflow → Choose log count → Run

## Features

✅ **Automated Daily Generation** - Runs automatically every day
✅ **Manual Trigger** - Run anytime from GitHub UI  
✅ **Configurable Count** - Adjust number of logs per run
✅ **Error Reporting** - Clear success/failure messages
✅ **Zero Cost** - Uses GitHub's free Actions minutes (2000/month)

## Cost Estimate

- **Execution Time**: ~30-60 seconds per run
- **Monthly Usage**: ~15-30 minutes (30 days × 1 minute)
- **Cost**: **FREE** (well under the 2000 minute limit)

## Next Steps

1. ✅ Add `DATABASE_URL` to GitHub Secrets
2. ✅ Test the workflow with "Run workflow"
3. ✅ Verify logs appear in your Railway database
4. ✅ Sit back and let it run automatically! 🎉

