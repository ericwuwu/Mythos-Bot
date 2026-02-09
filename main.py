import os
import random
import discord
from discord.ext import commands

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

# Base deck for each player
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

# Store player decks and hands separately
player_decks = {}  # Each player's custom deck
player_hands = {}  # Each player's current hand (4 cards)

def draw_from_deck(deck):
    """Draw 4 random cards from a deck"""
    if len(deck) < 4:
        # If deck has less than 4 cards, add duplicates
        while len(deck) < 4:
            deck.append(random.choice(deck))
    return random.sample(deck, 4)

def format_cards(cards, title="Cards"):
    """Format cards into a numbered list"""
    if not cards:
        return f"**{title}:**\n*No cards*"
    
    text = f"**{title}:**\n"
    for i, card in enumerate(cards, 1):
        text += f"{i}. {card}\n"
    return text

def get_player_deck(user_id):
    """Get or create a player's deck"""
    if user_id not in player_decks:
        # Start with a copy of the base deck
        player_decks[user_id] = BASE_DECK.copy()
    return player_decks[user_id]

@bot.event
async def on_ready():
    print(f'✅ Bot ready: {bot.user}')

# ===== DECK MANAGEMENT COMMANDS =====

@bot.command()
async def cards(ctx):
    """Show your custom deck"""
    user_id = str(ctx.author.id)
    deck = get_player_deck(user_id)
    
    if not deck:
        await ctx.send("Your deck is empty! Add cards with `$add [card name]`")
        return
    
    await ctx.send(format_cards(deck, "Your Deck"))

@bot.command()
async def add(ctx, *, card_text: str):
    """Add a card to your deck: $add Fire - 3 Mp"""
    user_id = str(ctx.author.id)
    deck = get_player_deck(user_id)
    
    # Clean up the input
    card_text = card_text.strip()
    
    if not card_text:
        await ctx.send("Please specify a card to add: `$add Fire - 3 Mp`")
        return
    
    # Add the card
    deck.append(card_text)
    
    await ctx.send(f"✅ Added: `{card_text}`\nYour deck now has {len(deck)} cards.")

@bot.command()
async def remove(ctx, card_number: int):
    """Remove a card from your deck: $remove 3"""
    user_id = str(ctx.author.id)
    deck = get_player_deck(user_id)
    
    if not deck:
        await ctx.send("Your deck is empty!")
        return
    
    if card_number < 1 or card_number > len(deck):
        await ctx.send(f"Please use a number between 1 and {len(deck)}")
        return
    
    # Remove the card (1-based index for user, 0-based for list)
    removed_card = deck.pop(card_number - 1)
    
    await ctx.send(f"✅ Removed: `{removed_card}`\nYour deck now has {len(deck)} cards.")

# ===== CARD GAME COMMANDS =====

@bot.command()
async def d(ctx):
    """Draw 4 cards from your deck"""
    user_id = str(ctx.author.id)
    deck = get_player_deck(user_id)
    
    if len(deck) < 4:
        await ctx.send(f"❌ You need at least 4 cards in your deck! (You have {len(deck)})")
        await ctx.send("Add more cards with `$add [card name]`")
        return
    
    # Draw 4 random cards from player's deck
    hand = draw_from_deck(deck)
    player_hands[user_id] = hand
    
    await ctx.send(format_cards(hand, "Your Hand"))

@bot.command()
async def x(ctx, *card_numbers):
    """Replace cards in your hand: $x 1 3"""
    user_id = str(ctx.author.id)
    
    if user_id not in player_hands:
        await ctx.send("Use `$d` first to draw a hand!")
        return
    
    if not card_numbers:
        await ctx.send("Specify which cards to replace: `$x 1 3`")
        return
    
    deck = get_player_deck(user_id)
    hand = player_hands[user_id].copy()
    
    try:
        for num in card_numbers:
            idx = int(num) - 1
            if 0 <= idx < 4:
                # Replace with random card from player's deck
                available_cards = [card for card in deck if card not in hand]
                if available_cards:
                    hand[idx] = random.choice(available_cards)
                else:
                    # If all cards are in hand, draw any from deck
                    hand[idx] = random.choice(deck)
        
        player_hands[user_id] = hand
        await ctx.send(format_cards(hand, "Your Hand"))
    except ValueError:
        await ctx.send("Use numbers 1-4: `$x 1 3`")

@bot.command()
async def show(ctx):
    """Show your current hand"""
    user_id = str(ctx.author.id)
    if user_id in player_hands:
        await ctx.send(format_cards(player_hands[user_id], "Your Hand"))
    else:
        await ctx.send("No hand! Use `$d` first to draw cards.")

@bot.command()
async def clear(ctx):
    """Clear your custom deck (reset to base)"""
    user_id = str(ctx.author.id)
    player_decks[user_id] = BASE_DECK.copy()
    await ctx.send("✅ Deck cleared! Reset to base deck.")

# ===== HELP COMMAND =====

@bot.command()
async def helpme(ctx):
    """Show all commands"""
    help_text = f"""
**🎴 CARD GAME BOT 🎴**

**DECK MANAGEMENT:**
`{ctx.prefix}cards` - Show your custom deck
`{ctx.prefix}add [card]` - Add a card to your deck
`{ctx.prefix}remove [number]` - Remove a card from your deck
`{ctx.prefix}clear` - Reset deck to base

**GAME PLAY:**
`{ctx.prefix}d` - Draw 4 cards from your deck
`{ctx.prefix}x 1 3` - Replace cards in your hand
`{ctx.prefix}show` - Show your current hand

**OTHER FEATURES:**
`roll d20` - Roll a dice
`:sob:` - Get 'L' response

**BASE DECK:** {len(BASE_DECK)} cards
- Elements: Fire, Wind, Water, Earth (3 Mp each)
- Spells: Ball, Bolt (2 Mp), Wall, Burst (3 Mp)
- Moves: Forward, Down (1 Mp), Orbit, Split (2 Mp)

**EXAMPLES:**
1. `{ctx.prefix}add Reverse - cost of what it's reversing`
2. `{ctx.prefix}d` - Draw 4 cards
3. `{ctx.prefix}x 1` - Replace card 1
4. `{ctx.prefix}remove 3` - Remove 3rd card from deck
"""
    await ctx.send(help_text)

# ===== OTHER FEATURES =====

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Dice roll
    if message.content.lower().startswith('roll d20'):
        r = random.randint(1, 20)
        if r == 1:
            response = f'🎲 Rolled **{r}** - Critical fail!'
        elif r == 20:
            response = f'🎲 Rolled **{r}** - NATURAL 20! 🎉'
        elif r < 10:
            response = f'🎲 Rolled **{r}** - get fucked lmao!'
        else:
            response = f'🎲 Rolled **{r}** - not bad!'
        await message.channel.send(response)
    
    # Sob emoji
    if ":sob:" in message.content:
        await message.channel.send("L")
    
    # Process commands
    await bot.process_commands(message)

# ===== RUN BOT =====

TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    print("❌ ERROR: Set DISCORD_TOKEN environment variable!")
    print("In Railway: Variables → Add DISCORD_TOKEN")
else:
    bot.run(TOKEN)
