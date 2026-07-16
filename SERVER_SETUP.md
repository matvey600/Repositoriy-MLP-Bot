# Server Setup

This guide is for running MLPCompanion 24/7 on an Ubuntu VPS, including Oracle Cloud Free Tier.

## Recommended VM

- OS: Ubuntu 24.04
- CPU: 1 OCPU is enough for a first run
- RAM: 1-2 GB is enough for the bot
- Disk: 50 GB is fine on Oracle because it is their server disk, not your PC disk

## 1. Create The Server

In Oracle Cloud, create an Ubuntu VM and download the private SSH key.

You need:

- public IP address
- SSH username, usually `ubuntu`
- private SSH key file

## 2. Connect From Windows

Open PowerShell in the folder where the SSH key is stored:

```powershell
ssh -i .\ssh-key.key ubuntu@SERVER_PUBLIC_IP
```

If Windows complains about key permissions, run:

```powershell
icacls .\ssh-key.key /inheritance:r
icacls .\ssh-key.key /grant:r "$env:USERNAME:R"
```

Then connect again.

## 3. Install The Bot

On the server:

```bash
git clone https://github.com/matvey600/Repositoriy-MLP-Bot.git
cd Repositoriy-MLP-Bot
sudo bash deploy/install_ubuntu.sh
```

## 4. Add Secrets

Edit the private server `.env`:

```bash
sudo nano /opt/mlpcompanion/.env
```

Fill:

```env
BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=
```

Save in nano:

- `Ctrl+O`
- `Enter`
- `Ctrl+X`

## 5. Start The Bot

```bash
sudo systemctl start mlpcompanion
sudo systemctl status mlpcompanion --no-pager
```

Live logs:

```bash
sudo journalctl -u mlpcompanion -f
```

## 6. Update Later

After pushing code changes to GitHub:

```bash
cd /opt/mlpcompanion
sudo bash deploy/update_ubuntu.sh
```

## Useful Commands

Stop:

```bash
sudo systemctl stop mlpcompanion
```

Restart:

```bash
sudo systemctl restart mlpcompanion
```

Check logs:

```bash
sudo journalctl -u mlpcompanion -n 100 --no-pager
```

