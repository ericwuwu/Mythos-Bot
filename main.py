import os
import random
import discord
from discord.ext import commands
from typing import Optional
import json
import traceback

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

# Base deck
BASE_DECK = [
    "Fire - 3 Mp",
    "Wind - 3 Mp", 
    "Water - 3 Mp",
    "Earth - 3 Mp",
    "Ball - 2 Mp",
    "Bolt - 2 Mp",
    "Wall - 3 Mp",
    "Burst - 3 Mp",
    "Forward - 1 Mp",
    "Down - 1 Mp",
    "Orbit - 2 Mp",
    "Split - 2 Mp"
]

# File for data persistence
DATA_FILE = "player_data.json"

# Player data structure
player_data = {}

def load_data():
    """Load player data from file"""
    global player_data
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                player_data = json.load(f)
            print(f"✅ Loaded data for {len(player_data)} players")
        else:
            print("📁 No existing data file found, starting fresh")
            player_data = {}
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        player_data = {}

def save_data():
    """Save player data to file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(player_data, f, indent=2)
        print("💾 Data saved")
    except Exception as e:
        print(f"❌ Error saving data: {e}")

def create_default_player():
    """Create a default player structure"""
    return {
        "current_deck": "1",
        "decks": {
            "1": {
                "name": "Deck 1",
                "cards": BASE_DECK.copy(),
                "hand_size": 6,
                "max_mp": 10,
                "current_mp": 10,
                "stats": "",
                "hand": []
            },
            "2": {
                "name": "Deck 2",
                "cards": [],
                "hand_size": 6,
                "max_mp": 10,
                "current_mp": 10,
                "stats": "",
                "hand": []
            },
            "3": {
                "name": "Deck 3",
                "cards": [],
                "hand_size": 6,
                "max_mp": 10,
                "current_mp": 10,
                "stats": "",
                "hand": []
            },
            "4": {
                "name": "Deck 4",
                "cards": [],
                "hand_size": 6,
                "max_mp": 10,
                "current_mp": 10,
                "stats": "",
                "hand": []
            },
            "5": {
                "name": "Deck 5",
                "cards": [],
                "hand_size": 6,
                "max_mp": 10,
                "current_mp": 10,
                "stats": "",
                "hand": []
            }
        }
    }

def get_player(user_id):
    """Get or create player data"""
    user_id = str(user_id)
    if user_id not in player_data:
        player_data[user_id] = create_default_player()
        save_data()
        print(f"✅ Created new player: {user_id}")
    return player_data[user_id]

def get_current_deck(user_id):
    """Get current deck for a user"""
    player = get_player(user_id)
    deck_num = player["current_deck"]
    
    # Ensure the deck exists (for legacy data)
    if deck_num not in player["decks"]:
        print(f"⚠️ Deck {deck_num} not found for {user_id}, resetting to deck 1")
        player["current_deck"] = "1"
        deck_num = "1"
    
    return player["decks"][deck_num]

def is_admin(ctx):
    """Check if user is admin"""
    return ctx.author.guild_permissions.administrator

@bot.event
async def on_ready():
    load_data()
    print(f'✅ Bot ready: {bot.user}')
    print(f'✅ Servers: {len(bot.guilds)}')
    print(f'✅ Use $helpme for commands')

@bot.event
async def on_command_error(ctx, error):
    """Global error handler"""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument: {error}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Invalid argument: {error}")
    elif isinstance(error, commands.CommandNotFound):
        # Ignore unknown commands
        pass
    else:
        # Log the error
        print(f"❌ Error in command {ctx.command}: {error}")
        traceback.print_exc()
        await ctx.send(f"❌ An error occurred. Check the logs.")

# ===== SIMPLE TEST COMMAND =====

@bot.command()
async def ping(ctx):
    """Simple test command"""
    await ctx.send("🏓 Pong! Bot is working.")

@bot.command()
async def test(ctx):
    """Test if player data is working"""
    try:
        player = get_player(ctx.author.id)
        deck = get_current_deck(ctx.author.id)
        await ctx.send(f"✅ Player data working! Current deck: {deck['name']} with {len(deck['cards'])} cards")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")
        print(f"Test command error: {e}")
        traceback.print_exc()

# ===== DECK MANAGEMENT =====

@bot.command()
async def deck(ctx, action: str, member: Optional[discord.Member] = None):
    """Switch or reset decks: $deck 2, $deck 3 @player, or $deck reset"""
    try:
        if action.lower() == "reset":
            target = member or ctx.author
            
            if member and not is_admin(ctx):
                await ctx.send("❌ Only admins can reset other players' decks!")
                return
            
            player = get_player(target.id)
            deck_num = player["current_deck"]
            deck = player["decks"][deck_num]
            
            # Reset deck to defaults
            deck["name"] = f"Deck {deck_num}"
            deck["cards"] = [] if deck_num != "1" else BASE_DECK.copy()
            deck["hand_size"] = 6
            deck["max_mp"] = 10
            deck["current_mp"] = 10
            deck["stats"] = ""
            deck["hand"] = []
            
            save_data()
            
            if target.id == ctx.author.id:
                await ctx.send(f"✅ Reset your Deck {deck_num} to default settings")
            else:
                await ctx.send(f"✅ Admin reset {target.display_name}'s Deck {deck_num} to default settings")
            return
        
        # Handle deck switching (numeric)
        try:
            deck_num = int(action)
        except ValueError:
            await ctx.send("❌ Use: `$deck 2`, `$deck 3 @player`, or `$deck reset`")
            return
        
        target = member or ctx.author
        
        if member and not is_admin(ctx):
            await ctx.send("❌ Only admins can switch other players' decks!")
            return
        
        if deck_num < 1 or deck_num > 5:
            await ctx.send("❌ Deck number must be between 1 and 5!")
            return
        
        player = get_player(target.id)
        old_deck = player["current_deck"]
        player["current_deck"] = str(deck_num)
        
        # Reset hand and MP when switching decks
        current = get_current_deck(target.id)
        current["hand"] = []
        current["current_mp"] = current["max_mp"]
        
        save_data()
        
        if target.id == ctx.author.id:
            await ctx.send(f"✅ Switched from Deck {old_deck} to Deck {deck_num} ({current['name']})")
        else:
            await ctx.send(f"✅ Admin switched {target.display_name} from Deck {old_deck} to Deck {deck_num} ({current['name']})")
    
    except Exception as e:
        print(f"Error in deck command: {e}")
        traceback.print_exc()
        await ctx.send(f"❌ Error in deck command. Check logs.")

@bot.command()
async def cards(ctx, member: Optional[discord.Member] = None):
    """Show deck cards: $cards or $cards @player"""
    try:
        target = member or ctx.author
        current = get_current_deck(target.id)
        
        if not current["cards"]:
            await ctx.send(f"{target.display_name}'s current deck is empty!")
            return
        
        response = f"**{target.display_name}'s {current['name']}** ({len(current['cards'])} cards):\n"
        for i, card in enumerate(current["cards"], 1):
            response += f"{i}. {card}\n"
        
        # Handle long messages
        if len(response) > 2000:
            await ctx.send(f"**{target.display_name}'s {current['name']}** (Part 1):")
            part = ""
            for i, card in enumerate(current["cards"], 1):
                if len(part) + len(f"{i}. {card}\n") > 1900:
                    await ctx.send(part)
                    part = ""
                part += f"{i}. {card}\n"
            if part:
                await ctx.send(part)
        else:
            await ctx.send(response)
    
    except Exception as e:
        print(f"Error in cards command: {e}")
        traceback.print_exc()
        await ctx.send(f"❌ Error in cards command.")

@bot.command()
async def draw(ctx, member: Optional[discord.Member] = None):
    """Draw a hand: $draw or $draw @player (admin only for others)"""
    try:
        target = member or ctx.author
        
        if member and not is_admin(ctx):
            await ctx.send("❌ Only admins can draw for other players!")
            return
        
        current = get_current_deck(target.id)
        
        if len(current["cards"]) < current["hand_size"]:
            await ctx.send(f"❌ {target.display_name} needs at least {current['hand_size']} cards in their deck! (Has {len(current['cards'])})")
            return
        
        # Draw hand
        current["hand"] = random.sample(current["cards"], current["hand_size"])
        save_data()
        
        # Show hand with MP
        response = f"**{target.display_name}'s {current['name']}** - MP: {current['current_mp']}/{current['max_mp']}\n"
        for i, card in enumerate(current["hand"], 1):
            response += f"{i}. {card}\n"
        
        await ctx.send(response)
    
    except Exception as e:
        print(f"Error in draw command: {e}")
        traceback.print_exc()
        await ctx.send(f"❌ Error in draw command.")

@bot.command()
async def hand(ctx, member: Optional[discord.Member] = None):
    """Show current hand: $hand or $hand @player"""
    try:
        target = member or ctx.author
        current = get_current_deck(target.id)
        
        if not current["hand"]:
            await ctx.send(f"{target.display_name} hasn't drawn a hand yet!")
            return
        
        response = f"**{target.display_name}'s {current['name']}** - MP: {current['current_mp']}/{current['max_mp']}\n"
        for i, card in enumerate(current["hand"], 1):
            response += f"{i}. {card}\n"
        
        await ctx.send(response)
    
    except Exception as e:
        print(f"Error in hand command: {e}")
        traceback.print_exc()
        await ctx.send(f"❌ Error in hand command.")

@bot.command()
async def r(ctx):
    """Roll d20: $r"""
    try:
        roll = random.randint(1, 20)
        if roll == 1:
            response = f'🎲 Rolled **{roll}** - Critical fail!'
        elif roll == 20:
            response = f'🎲 Rolled **{roll}** - NATURAL 20! 🎉'
        elif roll < 10:
            response = f'🎲 Rolled **{roll}** - get fucked lmao!'
        else:
            response = f'🎲 Rolled **{roll}** - not bad!'
        await ctx.send(response)
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command()
async def add(ctx, *, text: str):
    """Add a card: $add Fire - 3 Mp"""
    try:
        current = get_current_deck(ctx.author.id)
        current["cards"].append(text)
        save_data()
        await ctx.send(f"✅ Added: `{text}`\nDeck now has {len(current['cards'])} cards.")
    except Exception as e:
        print(f"Error in add command: {e}")
        await ctx.send(f"❌ Error in add command.")

@bot.command()
async def remove(ctx, card_number: int):
    """Remove a card: $remove 3"""
    try:
        current = get_current_deck(ctx.author.id)
        
        if not current["cards"]:
            await ctx.send("Your deck is empty!")
            return
        
        if card_number < 1 or card_number > len(current["cards"]):
            await ctx.send(f"Please use a number between 1 and {len(current['cards'])}")
            return
        
        removed = current["cards"].pop(card_number - 1)
        save_data()
        await ctx.send(f"✅ Removed: `{removed}`\nDeck now has {len(current['cards'])} cards.")
    
    except Exception as e:
        print(f"Error in remove command: {e}")
        await ctx.send(f"❌ Error in remove command.")

@bot.command()
async def settings(ctx):
    """View your current settings"""
    try:
        current = get_current_deck(ctx.author.id)
        response = f"**{ctx.author.display_name}'s {current['name']} Settings:**\n"
        response += f"• Hand Size: {current['hand_size']}\n"
        response += f"• Max MP: {current['max_mp']}\n"
        response += f"• Current MP: {current['current_mp']}/{current['max_mp']}\n"
        response += f"• Cards in Deck: {len(current['cards'])}"
        await ctx.send(response)
    except Exception as e:
        print(f"Error in settings command: {e}")
        await ctx.send(f"❌ Error in settings command.")

@bot.command()
async def helpme(ctx):
    """Show all commands"""
    help_text = """
**🎴 CARD GAME BOT - COMMANDS 🎴**

**TEST COMMANDS:**
`$ping` - Test if bot is working
`$test` - Test player data

**DECK MANAGEMENT:**
`$cards` - Show your current deck
`$add [card]` - Add a card
`$remove [#]` - Remove a card
`$draw` - Draw a hand
`$hand` - Show your hand
`$deck 2` - Switch to deck 2
`$deck reset` - Reset current deck
`$settings` - View your settings

**OTHER:**
`$r` - Roll d20
`$helpme` - This message

**DATA:** Auto-saves to file
"""
    await ctx.send(help_text)

# ===== RUN BOT =====

TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    print("❌ ERROR: Set DISCORD_TOKEN environment variable!")
    print("In Railway: Variables → Add DISCORD_TOKEN")
else:
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
