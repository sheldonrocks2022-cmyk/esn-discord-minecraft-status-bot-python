"""ESN Minecraft server status bot (Python, discord.py 2 + mcstatus). MIT License. https://esnoffical.com"""
import asyncio
import os
from typing import Literal

import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv
from mcstatus import BedrockServer, JavaServer

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
# Optional auto-updating status embed
STATUS_CHANNEL_ID = int(os.getenv("STATUS_CHANNEL_ID") or 0)
STATUS_HOST = os.getenv("STATUS_HOST", "").strip()
STATUS_EDITION = os.getenv("STATUS_EDITION", "java").strip().lower()
STATUS_INTERVAL = max(30, int(os.getenv("STATUS_INTERVAL", "60")))
STATUS_MESSAGE_FILE = os.getenv("STATUS_MESSAGE_FILE", "status_message_id.txt")
COLOR = 0x6C5CE7
OFFLINE_COLOR = 0xE74C3C
TIMEOUT = 5


async def query(host: str, edition: str) -> dict:
    """Ping a server and return a simple dict. Raises on failure."""
    if edition == "bedrock":
        server = BedrockServer.lookup(host, timeout=TIMEOUT)
        s = await server.async_status()
        return {
            "edition": "Bedrock", "online": s.players.online, "max": s.players.max,
            "version": s.version.name, "motd": s.motd.to_plain(), "latency": s.latency, "sample": [],
        }
    try:
        server = await JavaServer.async_lookup(host, timeout=TIMEOUT)  # follows SRV records
    except Exception:
        # Some DNS setups fail the SRV lookup; fall back to host:port directly
        name, _, port = host.rpartition(":") if ":" in host else (host, "", "")
        server = JavaServer(name, int(port) if port.isdigit() else 25565, timeout=TIMEOUT)
    s = await server.async_status()
    return {
        "edition": "Java", "online": s.players.online, "max": s.players.max,
        "version": s.version.name, "motd": s.motd.to_plain(), "latency": s.latency,
        "sample": [p.name for p in (s.players.sample or [])],
    }


async def query_auto(host: str, edition: str) -> dict:
    if edition in ("java", "bedrock"):
        return await query(host, edition)
    try:  # auto: try Java first, then Bedrock
        return await query(host, "java")
    except Exception:
        return await query(host, "bedrock")


def status_embed(host: str, info: dict | None) -> discord.Embed:
    if info is None:
        e = discord.Embed(title=f"🔴 {host}", description="Server is **offline** or not reachable.", color=OFFLINE_COLOR)
    else:
        motd = discord.utils.escape_markdown(info["motd"].strip())[:300] or "No MOTD"
        e = discord.Embed(title=f"🟢 {host}", description=f"```\n{motd}\n```", color=COLOR)
        e.add_field(name="Players", value=f"{info['online']}/{info['max']}")
        e.add_field(name="Version", value=discord.utils.escape_markdown(str(info["version"]))[:100] or "?")
        e.add_field(name="Edition", value=info["edition"])
        e.add_field(name="Ping", value=f"{round(info['latency'])} ms")
        if info["sample"]:
            names = ", ".join(discord.utils.escape_markdown(n) for n in info["sample"][:12])
            e.add_field(name="Online now", value=names[:1000], inline=False)
    e.timestamp = discord.utils.utcnow()
    e.set_footer(text="Minecraft server status")
    return e


class StatusBot(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()
        if STATUS_CHANNEL_ID and STATUS_HOST:
            auto_status.change_interval(seconds=STATUS_INTERVAL)
            auto_status.start()


bot = StatusBot()


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user} ({bot.user.id})")


@bot.tree.command(name="mcstatus", description="Check a Minecraft server's status (Java or Bedrock)")
@app_commands.describe(host="Server address, e.g. play.example.com or 1.2.3.4:25565", edition="Java, Bedrock or auto-detect")
async def mcstatus_command(interaction: discord.Interaction, host: app_commands.Range[str, 3, 255],
                           edition: Literal["auto", "java", "bedrock"] = "auto") -> None:
    await interaction.response.defer()
    host = host.strip()
    try:
        info = await asyncio.wait_for(query_auto(host, edition), timeout=TIMEOUT * 3)
    except Exception:
        info = None
    await interaction.followup.send(embed=status_embed(host, info))


@tasks.loop(seconds=60)
async def auto_status() -> None:
    """Keeps one embed in STATUS_CHANNEL_ID up to date (edits it instead of spamming new messages)."""
    channel = bot.get_channel(STATUS_CHANNEL_ID)
    if not isinstance(channel, discord.TextChannel):
        return
    try:
        info = await asyncio.wait_for(query_auto(STATUS_HOST, STATUS_EDITION), timeout=TIMEOUT * 3)
    except Exception:
        info = None
    embed = status_embed(STATUS_HOST, info)

    msg_id = None
    if os.path.exists(STATUS_MESSAGE_FILE):
        try:
            msg_id = int(open(STATUS_MESSAGE_FILE).read().strip())
        except ValueError:
            msg_id = None
    if msg_id:
        try:
            msg = await channel.fetch_message(msg_id)
            await msg.edit(embed=embed)
            return
        except discord.NotFound:
            pass  # deleted, post a new one
    msg = await channel.send(embed=embed)
    with open(STATUS_MESSAGE_FILE, "w") as f:
        f.write(str(msg.id))


@auto_status.before_loop
async def before_auto_status() -> None:
    await bot.wait_until_ready()


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("Set DISCORD_TOKEN in .env first.")
    bot.run(TOKEN)
