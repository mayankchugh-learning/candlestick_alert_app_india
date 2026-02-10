# Email Setup Guide - SMTP Configuration

The application now uses Python backend SMTP for sending email notifications instead of EmailJS.

## Gmail Setup (Recommended)

### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account: https://myaccount.google.com/
2. Navigate to **Security** → **2-Step Verification**
3. Follow the steps to enable 2FA

### Step 2: Generate App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Select **Mail** and **Other (Custom name)**
3. Enter "CandleAlert" as the name
4. Click **Generate**
5. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

### Step 3: Configure .env File
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=abcdefghijklmnop
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

## Other Email Providers

### Outlook/Hotmail
```env
MAIL_SERVER=smtp.office365.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-password
MAIL_DEFAULT_SENDER=your-email@outlook.com
```

### Yahoo Mail
```env
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@yahoo.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@yahoo.com
```

### Custom SMTP Server
```env
MAIL_SERVER=smtp.yourprovider.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-username
MAIL_PASSWORD=your-password
MAIL_DEFAULT_SENDER=sender@yourprovider.com
```

## Application Configuration

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Settings in Dashboard
1. Open the application: http://localhost:5000
2. Go to **Settings** tab
3. Enter your **Recipient Email** (where alerts will be sent)
4. Check **Enable automatic email alerts**
5. Click **Save Settings**

### 3. Test Email
1. Click **Send Test** button in Settings
2. Check your inbox for the test email
3. If successful, you'll see a success message

## Email Notification Features

### Automatic Alerts
- Emails are sent automatically when new trading signals are detected
- Triggered during manual scans and scheduled monthly scans
- Contains summary of buy/sell signals with stock details

### Email Content
- Total alerts count
- Top 10 buy signals with prices and strength
- Top 10 sell signals with prices and strength
- Direct link to dashboard

## Troubleshooting

### "Authentication failed" Error
- **Gmail**: Make sure you're using an App Password, not your regular password
- **Outlook**: Enable "Less secure app access" in account settings
- **Yahoo**: Generate and use an App Password

### "Connection refused" Error
- Check if MAIL_SERVER and MAIL_PORT are correct
- Verify your firewall isn't blocking SMTP connections
- Try using port 465 with SSL instead of 587 with TLS

### "Sender address rejected" Error
- Ensure MAIL_USERNAME matches MAIL_DEFAULT_SENDER
- Some providers require the sender to be the authenticated user

### Test Email Not Received
- Check spam/junk folder
- Verify recipient email is correct
- Check application logs for error messages

## Security Best Practices

1. **Never commit .env file** to version control
2. **Use App Passwords** instead of account passwords
3. **Rotate passwords** regularly
4. **Limit access** to .env file on production servers
5. **Use environment variables** in cloud deployments

## Production Deployment

### Heroku
```bash
heroku config:set MAIL_SERVER=smtp.gmail.com
heroku config:set MAIL_PORT=587
heroku config:set MAIL_USE_TLS=True
heroku config:set MAIL_USERNAME=your-email@gmail.com
heroku config:set MAIL_PASSWORD=your-app-password
```

### Docker
```bash
docker run -d \
  -e MAIL_SERVER=smtp.gmail.com \
  -e MAIL_PORT=587 \
  -e MAIL_USE_TLS=True \
  -e MAIL_USERNAME=your-email@gmail.com \
  -e MAIL_PASSWORD=your-app-password \
  candlestick-alert
```

## Support

If you encounter issues:
1. Check application logs: `docker-compose logs -f app`
2. Verify SMTP settings in .env file
3. Test with a simple email client first
4. Check provider-specific documentation
