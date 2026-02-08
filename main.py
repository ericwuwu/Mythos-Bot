import os
import random
import discord
from discord.ext import commands

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Cards
CARDS = [
    "Fire - 3 Mp", "Wind - 3 Mp", "Water - 3 Mp", "Earth - 3 Mp",
    "Null - 1 Mp", "Ball - 2 Mp", "Bolt - 2 Mp", "Wall - 3 Mp",
    "Burst - 3 Mp", "Forward - 1 Mp", "Down - 1 Mp", "Orbit - 2 Mp",
    "Split - 2 Mp", "Reverse - cost of what it's reversing"
]

hands = {}

def draw():
    return random.sample(CARDS, 4)

def show(cards):
    text = "**Cards:**\n"
    for i, card in enumerate(cards, 1):
        text += f"{i}. {card}\n"
    return text

@bot.event
async def on_ready():
    print(f'✅ Bot ready: {bot.user}')

@bot.command()
async def d(ctx):
    hands[str(ctx.author.id)] = draw()
    await ctx.send(show(hands[str(ctx.author.id)]))

@bot.command()
async def x(ctx, *nums):
    user = str(ctx.author.id)
    if user not in hands:
        await ctx.send("Use /d first!")
        return
    cards = hands[user].copy()
    for n in nums:
        i = int(n) - 1
        if 0 <= i < 4:
            cards[i] = random.choice(CARDS)
    hands[user] = cards
    await ctx.send(show(cards))

@bot.command()
async def showcmd(ctx):
    user = str(ctx.author.id)
    if user in hands:
        await ctx.send(show(hands[user]))
    else:
        await ctx.send("Use /d first")

@bot.command()
async def helpme(ctx):
    text = """**Commands:**
/d - Draw 4 cards
/x 1 3 - Replace cards 1 and 3
/show - See your cards
/helpme - This message"""
    await ctx.send(text)

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return
    if msg.content.startswith('roll d20'):
        r = random.randint(1, 20)
        await msg.channel.send(f'🎲 Rolled: {r}')
    if ":sob:" in msg.content:
        await msg.channel.send("L")
    await bot.process_commands(msg)

# Get token from Railway environment variable
TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    print("❌ ERROR: Set DISCORD_TOKEN environment variable!")
else:
    bot.run(TOKEN)