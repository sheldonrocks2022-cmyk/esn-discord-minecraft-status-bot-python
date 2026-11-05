# ESN Discord Minecraft Status Bot (Python)

[![Deploy to ESN](https://panel.esnoffical.com/deploy/badge.svg)](https://panel.esnoffical.com/deploy?repo=https://github.com/sheldonrocks2022-cmyk/esn-discord-minecraft-status-bot-python)

A Discord bot in Python (discord.py 2) that shows the live status of any Minecraft server, Java or Bedrock, using the `mcstatus` library. Made by [ESN Hosting](https://esnoffical.com/?utm_source=github&utm_medium=readme&utm_campaign=bot-templates).

## What it does

- `/mcstatus <host> [edition]` shows online/offline, players, version, MOTD and ping for Java or Bedrock (or auto-detect)
- Shows who is online when the Java server shares a player sample
- Optional status channel: one embed that updates itself every minute (it edits the same message, no spam)
- Uses the normal server list ping, so it never joins the server

## Setup

1. Create an app at https://discord.com/developers/applications. Under **Bot**, click **Reset Token** and copy it.
2. Invite the bot with the `bot` and `applications.commands` scopes and the **View Channels**, **Send Messages**, **Embed Links** and **Read Message History** permissions (OAuth2 > URL Generator). No privileged intents needed.
3. Copy `.env.example` to `.env` and fill it in (at least `DISCORD_TOKEN`).
4. Install and run:

```bash
pip install -r requirements.txt
python bot.py
```

## Files

- `bot.py`: the whole bot
- `requirements.txt`: discord.py, mcstatus and python-dotenv
- `.env.example`: copy to `.env` and fill in

Needs Python 3.10 or newer. Want to check a server from your browser instead? Try the [Minecraft server status checker](https://docs.esnoffical.com/minecraft-server-status-checker.html).

## Host it 24/7 on ESN Hosting

Your PC has to stay on for the bot to stay online. [ESN Hosting](https://esnoffical.com/?utm_source=github&utm_medium=readme&utm_campaign=bot-templates) keeps it running 24/7, with bot hosting from $0.50/month. Upload this folder in the panel's file manager, add your `.env` values and press Start. Step-by-step guide: [How to host a discord.py bot 24/7](https://docs.esnoffical.com/host-discord-py-bot-24-7.html).

Need help? Join the ESN Discord: https://discord.gg/RGPt3zEfGy

## License

MIT. See [LICENSE](LICENSE).
