# Hostinger DDNS - Dynamic DNS Client for Hostinger

A lightweight, self-hosted Dynamic DNS (DDNS) client for updating DNS records on Hostinger domains. Perfect for self-hosting enthusiasts who want to keep their domain's DNS pointing to a machine with a dynamic IP address.

**Features:**
- ✅ Automatic IP detection and DNS updates
- ✅ Prevents unnecessary API calls by caching last known IP
- ✅ Comprehensive logging for troubleshooting
- ✅ Easy configuration via `.env` file
- ✅ Lightweight and battery-friendly (runs in seconds)
- ✅ Ideal for Raspberry Pi, NAS, and other always-on devices

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [Setting Up Cron Job](#setting-up-cron-job)
6. [Troubleshooting](#troubleshooting)
7. [How It Works](#how-it-works)
8. [Contributing](#contributing)
9. [License](#license)

---

## Prerequisites

- **Python 3.9+** installed on your system
- **Hostinger account** with API access enabled
- **Hostinger API token** (see setup instructions below)
- **Internet connection** to access your Hostinger API
- A domain name hosted on Hostinger

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/hostinger-ddns.git
cd hostinger-ddns
```

Or download the latest release:
```bash
wget https://github.com/your-username/hostinger-ddns/releases/download/v1.0.0/hostinger-ddns.tar.gz
tar xzf hostinger-ddns.tar.gz
cd hostinger-ddns
```

### 2. Create Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Alternatively, install packages individually:
```bash
pip install requests hostinger-api python-dotenv
```

---

## Configuration

### 1. Get Your Hostinger API Token

1. Log in to your **hPanel** at https://hpanel.hostinger.com
2. Click on **Profile** (top right)
3. Navigate to **Account Information** → **API**
4. Generate a new API token
5. Copy the token (you won't see it again!)

**⚠️ Keep your API token secret!** Treat it like a password.

### 2. Set Up Environment File

Copy the example configuration:

```bash
cp .env.example .env
```

Edit `.env` with your details:

```env
# Your Hostinger API token (keep this secret!)
API_TOKEN=your_token_here

# Your domain name on Hostinger
DOMAIN=example.com

# The subdomain (A record) to update (use @ for root domain)
SUBDOMAIN=vpn

# TTL in seconds (lower = faster propagation, higher = fewer API calls)
TTL=60

# Where to store logs (ensure directory is writable)
LOG_FILE=/home/username/hostinger-ddns-python.log

# Temporary file to cache last known IP
LAST_IP_FILE=/tmp/hostinger-ddns-python-last-ip.txt
```

**⚠️ Important:** `.env` is in `.gitignore` and will never be committed to version control. Always keep your tokens private!

### Configuration Examples

#### For a Raspberry Pi (Always-On Device)

```env
API_TOKEN=your_api_token_here
DOMAIN=myserver.com
SUBDOMAIN=raspberry
TTL=300
LOG_FILE=/var/log/hostinger-ddns/ddns.log
LAST_IP_FILE=/tmp/hostinger-ddns-last-ip.txt
```

#### For Multiple Subdomains

Create separate clones of the repository:
```
hostinger-ddns/
├── hostinger-ddns-vpn/
│   ├── .env (SUBDOMAIN=vpn)
│   └── hostinger_ddns.py
└── hostinger-ddns-web/
    ├── .env (SUBDOMAIN=web)
    └── hostinger_ddns.py
```

---

## Usage

### Manual Execution

Run the script directly:

```bash
source venv/bin/activate
python hostinger_ddns.py
```

**Output:** Check the log file specified in your `.env` for results.

### View Logs

```bash
tail -f /home/username/hostinger-ddns-python.log
```

Example successful log:
```
[2025-10-27 22:00:01] INFO: Script started.
[2025-10-27 22:00:02] INFO: IP change detected. Current IP: 49.47.218.86, Last IP: None.
[2025-10-27 22:00:02] ACTION: Sending update request to Hostinger API for vpn.example.com -> 49.47.218.86
[2025-10-27 22:00:03] SUCCESS: Hostinger API accepted update for vpn.example.com to 49.47.218.86
[2025-10-27 22:00:03] INFO: Script finished. Update successful.
```

---

## Setting Up Cron Job

### For Linux/Raspberry Pi (Recommended)

Edit your crontab:
```bash
crontab -e
```

Add one of these lines (choose based on your needs):

**Every 5 minutes** (most common):
```cron
*/5 * * * * cd /home/ashwath/hostinger_ddns && source venv/bin/activate && python hostinger_ddns.py
```

**Every 10 minutes:**
```cron
*/10 * * * * cd /home/ashwath/hostinger_ddns && source venv/bin/activate && python hostinger_ddns.py
```

**Every hour:**
```cron
0 * * * * cd /home/ashwath/hostinger_ddns && source venv/bin/activate && python hostinger_ddns.py
```

**On boot (after 2 minute delay):**
```cron
@reboot sleep 120 && cd /home/ashwath/hostinger_ddns && source venv/bin/activate && python hostinger_ddns.py
```

### For NAS Devices

Consult your NAS's documentation for task scheduling. Examples:
- **Synology DSM:** Control Panel → Task Scheduler
- **QNAP NAS:** System Settings → System Tools → Scheduled Tasks
- **Unraid:** Scheduled Jobs plugin

### For Docker (Optional)

Create a simple cron container to run the script periodically.

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'hostinger_api'`

**Solution:** Ensure dependencies are installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: `ERROR: API_TOKEN is not set or invalid`

**Solution:** 
1. Check that `.env` file exists in the script directory
2. Verify `API_TOKEN` is set with your real token (not placeholder)
3. Ensure `.env` is readable by your user

```bash
ls -la .env
cat .env | grep API_TOKEN
```

### Issue: `ERROR: Authentication failed (401/403)`

**Solution:**
1. Verify your API token is correct in `.env`
2. Check if your token has expired (generate a new one)
3. Ensure your Hostinger account has API access enabled

### Issue: `ERROR: Validation error (422)`

**Solution:**
1. Verify `DOMAIN` exists on your Hostinger account
2. Check that `SUBDOMAIN` is correct (use `@` for root domain)
3. Ensure domain and subdomain names are lowercase

### Issue: `Permission denied` when writing logs

**Solution:**
1. Create the log directory manually:
   ```bash
   mkdir -p /var/log/hostinger-ddns
   sudo chown $USER:$USER /var/log/hostinger-ddns
   chmod 755 /var/log/hostinger-ddns
   ```
2. Or change `LOG_FILE` to a user-writable directory:
   ```env
   LOG_FILE=/home/username/hostinger-ddns.log
   ```

### Issue: Frequent "IP change detected" messages

**Solution:**
1. Check if your IP is actually changing:
   ```bash
   curl https://ifconfig.me
   ```
2. If IP is stable, the issue is likely with `LAST_IP_FILE` permissions:
   ```bash
   rm /tmp/hostinger-ddns-python-last-ip.txt
   python hostinger_ddns.py
   ```

### Enable Debug Mode

Add more verbose output by checking the full log:
```bash
tail -50 /home/username/hostinger-ddns-python.log | grep -i error
```

---

## How It Works

```
┌─────────────────────────────────────────────────────┐
│ Cron Job Executes (every 5 minutes)                 │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ 1. Fetch current public IP from ifconfig.me         │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ 2. Read last known IP from cache file               │
└─────────────────────────────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │ IP Changed?                   │
        └───────────────────────────────┘
               ↙                   ↘
           Yes                       No
            ↓                         ↓
      ┌──────────────────┐    ┌──────────────────┐
      │ Call Hostinger   │    │ Log: No update   │
      │ API to update    │    │ needed. Exit.    │
      │ DNS record       │    └──────────────────┘
      └──────────────────┘
            ↓
    ┌──────────────────┐
    │ Success?         │
    └──────────────────┘
        ↙          ↘
      Yes            No
       ↓              ↓
    ┌──────┐    ┌──────────┐
    │Save  │    │Log error,│
    │new IP│    │don't save│
    │Exit 0│    │Exit 1    │
    └──────┘    └──────────┘
```

**Key Benefits:**
- **Efficient:** Only calls API when IP changes
- **Reliable:** Comprehensive error logging
- **Safe:** Secret tokens kept in `.env`, never committed
- **Lightweight:** Runs in seconds, minimal resource usage

---

## Contributing

We welcome contributions from the self-hosting community!

### How to Contribute

1. **Fork the repository** on GitHub
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and test thoroughly
4. **Commit with clear messages:**
   ```bash
   git commit -m "Add feature: description of changes"
   ```
5. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Create a Pull Request** with a description of changes

### Ideas for Contribution

- Support for other DNS providers (Cloudflare, Linode, etc.)
- IPv6 support
- Systemd service file for automatic startup
- Docker image
- Configuration wizard for first-time setup
- Web UI for monitoring
- Support for multiple A records in one run
- Webhook notifications on IP change

---

## License

This project is licensed under the **MIT License** - see `LICENSE` file for details.

```
MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## Support

- **Issues:** GitHub Issues for bug reports and feature requests
- **Discussions:** GitHub Discussions for questions and ideas
- **Email:** For private security concerns

---

## Changelog

### v1.0.0 (2025-10-27)
- ✅ Initial release with Hostinger API v1 support
- ✅ Environment variable configuration via `.env`
- ✅ IP caching to reduce API calls
- ✅ Comprehensive logging
- ✅ Proper error handling and validation

---

## Self-Hosting Resources

- [awesome-selfhosted](https://github.com/awesome-selfhosted/awesome-selfhosted) - A list of Free Software network services and web applications
- [r/selfhosted](https://reddit.com/r/selfhosted) - Community for self-hosting enthusiasts
- [Hostinger API Documentation](https://www.hostinger.com/api)

---

**Happy self-hosting! 🚀**
