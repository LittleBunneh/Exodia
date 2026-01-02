# EXODIA Deployment Guide

## Quick Start (5 minutes)

### 1. Clone Repository
```bash
git clone https://github.com/LittleBunneh/Exodia.git
cd Exodia
```

### 2. Run Setup Script
```bash
python complete_setup.py
```

This will automatically:
- Check and install all dependencies
- Create necessary directories
- Initialize .env configuration file
- Test API connections

### 3. Configure Credentials
Edit `.env` file with your actual keys:
```bash
# Get from Supabase dashboard
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_actual_key

# Get from DeepSeek platform
DEEPSEEK_API_KEY=your_actual_key

# Get from PythonAnywhere
PYTHONANYWHERE_USERNAME=your_username
PYTHONANYWHERE_API_TOKEN=your_token
```

### 4. Test Locally (Optional)
```bash
python main.py
# Navigate to http://localhost:5000
```

## PythonAnywhere Deployment

### 1. Upload Repository
```bash
git clone https://github.com/LittleBunneh/Exodia.git /home/LittleBunnehGod/Exodia
cd /home/LittleBunnehGod/Exodia
```

### 2. Run Setup on PythonAnywhere
```bash
python3.11 complete_setup.py
```

### 3. Configure WSGI File
In PythonAnywhere Web tab, set WSGI config:
```python
# /var/www/littlebunnehgod_pythonanywhere_com_wsgi.py
import os
import sys

sys.path.insert(0, '/home/LittleBunnehGod/Exodia')
os.environ['PYTHON_ENV'] = 'production'

from main import app

application = app
```

### 4. Set Environment Variables
In PythonAnywhere Web app, add in "Web app settings":
- Post-code to run on load: `from dotenv import load_dotenv; load_dotenv()`

### 5. Configure SSL
- Domain: prometheanconduit.ai
- Use HTTPS (let's encrypt certificate)
- Force HTTPS redirect

### 6. Set Allowed Hosts
In main.py or config:
```python
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com', 'prometheanconduit.ai']
```

## Supabase Setup

### 1. Create Supabase Project
- Go to https://supabase.com
- New project: "Exodia"
- Region: Choose closest to your users

### 2. Create Tables
Run in Supabase SQL Editor:
```sql
CREATE TABLE user_memory (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NOT NULL UNIQUE,
  memory_data jsonb,
  updated_at timestamp DEFAULT NOW()
);

CREATE TABLE conversations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NOT NULL,
  user_message text,
  ai_response text,
  ai_model text DEFAULT 'DeepSeek',
  timestamp timestamp DEFAULT NOW()
);

CREATE INDEX conversations_user_id_idx ON conversations(user_id);
CREATE INDEX conversations_timestamp_idx ON conversations(timestamp DESC);
```

### 3. Enable Row Level Security (Optional)
```sql
ALTER TABLE user_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
```

## DeepSeek API Setup

### 1. Get API Key
- Go to https://platform.deepseek.com
- Login with your account
- Generate API key
- Copy to .env: `DEEPSEEK_API_KEY=...`

### 2. Test Connection
```bash
curl https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer YOUR_KEY"
```

## Domain Configuration

### Namecheap (prometheanconduit.ai)

1. **Point Domain to PythonAnywhere:**
   - Go to Namecheap → DNS settings
   - Add A record: `yourusername.pythonanywhere.com`

2. **Configure in PythonAnywhere:**
   - Web app settings
   - Add domain: `prometheanconduit.ai`
   - Add alternate: `www.prometheanconduit.ai`

3. **Enable SSL:**
   - PythonAnywhere → Web
   - Use "Let's Encrypt" certificate
   - Force HTTPS

## Monitoring & Logs

### View Application Logs
```bash
# On PythonAnywhere
tail -f /tmp/exodia.log
```

### Monitor Supabase
- Dashboard → Logs
- Database → Monitor

### Monitor DeepSeek Usage
- https://platform.deepseek.com/usage

## Troubleshooting

### Issue: "SUPABASE_KEY not found"
**Solution:** Make sure .env is in the project root and has correct format

### Issue: "DeepSeek API 401"
**Solution:** Check API key is correct and has funds/quota

### Issue: "PythonAnywhere 502 Bad Gateway"
**Solution:**
1. Check WSGI configuration
2. Review error logs: Web tab → Error log
3. Restart web app

## Maintenance

### Weekly
- Check error logs
- Monitor API usage
- Backup database: `pg_dump` Supabase DB

### Monthly
- Review conversation logs
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Test DeepSeek API connection

### Database Cleanup
```sql
-- Delete conversations older than 90 days
DELETE FROM conversations 
WHERE timestamp < NOW() - INTERVAL '90 days';
```

## Performance Tips

1. **Enable Caching:** Redis (if available)
2. **Optimize Queries:** Use database indexes
3. **Rate Limiting:** Implement per-user limits
4. **CDN:** Serve static files via CDN

## Security Checklist

- [ ] .env file is in .gitignore
- [ ] Never commit API keys
- [ ] Enable Supabase RLS policies
- [ ] Use HTTPS only
- [ ] Set strong database passwords
- [ ] Enable CORS only for your domain
- [ ] Monitor API quotas

## Support

For issues:
1. Check this guide
2. Review error logs
3. Visit PythonAnywhere help: https://www.pythonanywhere.com/help/
4. Visit Supabase docs: https://supabase.com/docs

---

**Exodia is live and ready to serve!**
