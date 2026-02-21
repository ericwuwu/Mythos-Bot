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
player_hands = {}  # Each player's current hand (6 cards)

def draw_from_deck(deck, count=6):
    """Draw X random cards from a deck"""
    if len(deck) < count:
        # If deck has less than X cards, add duplicates
        while len(deck) < count:
            deck.append(random.choice(deck))
    return random.sample(deck, count)

@bot.event
async def on_ready():
    print(f'✅ Bot ready: {bot.user}')

def get_player_deck(user_id):
    """Get or create a player's deck"""
    user_id = str(user_id)
    if user_id not in player_decks:
        # Start with a copy of the base deck
        player_decks[user_id] = BASE_DECK.copy()
    return player_decks[user_id]

# ===== DECK MANAGEMENT COMMANDS =====

@bot.command()
async def cards(ctx, member: discord.Member = None):
    """Show your custom deck or another player's deck: $cards @user"""
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    deck = get_player_deck(user_id)
    
    if not deck:
        await ctx.send(f"{member.display_name}'s deck is empty!")
        return
    
    # Show with player's name
    response = f"**{member.display_name}'s Deck** ({len(deck)} cards):\n"
    for i, card in enumerate(deck, 1):
        response += f"{i}. {card}\n"
    
    # Split long messages if needed
    if len(response) > 2000:
        # Send first part
        await ctx.send(f"**{member.display_name}'s Deck** ({len(deck)} cards) - Part 1:")
        part = ""
        for i, card in enumerate(deck, 1):
            if len(part) + len(f"{i}. {card}\n") > 1900:
                await ctx.send(part)
                part = ""
            part += f"{i}. {card}\n"
        if part:
            await ctx.send(part)
    else:
        await ctx.send(response)

@bot.command()
async def add(ctx, member: discord.Member, *, card_text: str):
    """Add a card to a player's deck: $add @user Fire - 3 Mp"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Only administrators can add cards to other players!")
        return
    
    user_id = str(member.id)
    deck = get_player_deck(user_id)
    
    # Clean up the input
    card_text = card_text.strip()
    
    if not card_text:
        await ctx.send(f"Please specify a card to add: `$add @user Fire - 3 Mp`")
        return
    
    # Add the card
    deck.append(card_text)
    
    await ctx.send(f"✅ Administrator added to {member.display_name}'s deck: `{card_text}`\nTheir deck now has {len(deck)} cards.")

@bot.command()
async def remove(ctx, member: discord.Member = None, card_number: int = None):
    """Remove a card from your deck or another player's deck (admin only): $remove @user 3"""
    if member is None:
        # Remove from self
        member = ctx.author
        target_id = str(ctx.author.id)
        deck = get_player_deck(target_id)
        
        if card_number is None:
            await ctx.send(f"Please specify a card number: `$remove 3`")
            return
    else:
        # Admin removing from another player
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Only administrators can remove cards from other players!")
            return
        
        if card_number is None:
            await ctx.send(f"Please specify a card number: `$remove @user 3`")
            return
        
        target_id = str(member.id)
        deck = get_player_deck(target_id)
    
    if not deck:
        await ctx.send(f"{member.display_name}'s deck is empty!")
        return
    
    if card_number < 1 or card_number > len(deck):
        await ctx.send(f"Please use a number between 1 and {len(deck)}")
        return
    
    # Remove the card (1-based index for user, 0-based for list)
    removed_card = deck.pop(card_number - 1)
    
    if member.id == ctx.author.id:
        await ctx.send(f"✅ Removed from your deck: `{removed_card}`\nYour deck now has {len(deck)} cards.")
    else:
        await ctx.send(f"✅ Administrator removed from {member.display_name}'s deck: `{removed_card}`\nTheir deck now has {len(deck)} cards.")

@bot.command()
async def clear(ctx, member: discord.Member = None):
    """Clear your custom deck or another player's deck (admin only): $clear @user"""
    if member is None:
        # Clear self
        user_id = str(ctx.author.id)
        player_decks[user_id] = BASE_DECK.copy()
        await ctx.send(f"✅ Your deck cleared! Reset to base deck.")
    else:
        # Admin clearing another player
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Only administrators can clear other players' decks!")
            return
        
        user_id = str(member.id)
        player_decks[user_id] = BASE_DECK.copy()
        await ctx.send(f"✅ Administrator cleared {member.display_name}'s deck! Reset to base deck.")

# ===== CARD GAME COMMANDS =====

@bot.command()
async def d(ctx):
    """Draw 6 cards from your deck"""
    user_id = str(ctx.author.id)
    deck = get_player_deck(user_id)
    
    if len(deck) < 6:
        await ctx.send(f"❌ {ctx.author.mention}, you need at least 6 cards in your deck! (You have {len(deck)})")
        await ctx.send(f"Add more cards with `$add [card name]`")
        return
    
    # Draw 6 random cards from player's deck
    hand = draw_from_deck(deck, 6)
    player_hands[user_id] = hand
    
    # Show with player's name
    response = f"**{ctx.author.display_name}'s Hand** (from their deck of {len(deck)} cards):\n"
    for i, card in enumerate(hand, 1):
        response += f"{i}. {card}\n"
    
    await ctx.send(response)

@bot.command()
async def hand(ctx, member: discord.Member = None):
    """Show your current hand or another player's hand: $hand @user"""
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    if user_id in player_hands:
        hand = player_hands[user_id]
        deck = get_player_deck(user_id)
        response = f"**{member.display_name}'s Current Hand** (from their deck of {len(deck)} cards):\n"
        for i, card in enumerate(hand, 1):
            response += f"{i}. {card}\n"
        await ctx.send(response)
    else:
        await ctx.send(f"{member.display_name} hasn't drawn a hand yet! Use `$d` first to draw cards.")

# Alias for hand command
@bot.command()
async def deck(ctx, member: discord.Member = None):
    """Alias for $hand - Show current hand: $deck @user"""
    await hand(ctx, member)

@bot.command()
async def x(ctx, *card_numbers):
    """Replace cards in your hand: $x 1 3 5"""
    user_id = str(ctx.author.id)
    
    if user_id not in player_hands:
        await ctx.send(f"{ctx.author.mention}, use `$d` first to draw a hand!")
        return
    
    if not card_numbers:
        await ctx.send(f"{ctx.author.mention}, specify which cards to replace: `$x 1 3 5`")
        return
    
    deck = get_player_deck(user_id)
    hand = player_hands[user_id].copy()
    replaced_indices = []
    
    try:
        for num in card_numbers:
            idx = int(num) - 1
            if 0 <= idx < 6:
                # Replace with random card from player's deck
                available_cards = [card for card in deck if card not in hand]
                if available_cards:
                    hand[idx] = random.choice(available_cards)
                else:
                    # If all cards are in hand, draw any from deck
                    hand[idx] = random.choice(deck)
                replaced_indices.append(int(num))
        
        player_hands[user_id] = hand
        
        # Show updated hand with player's name
        replaced_list = ", ".join(map(str, sorted(replaced_indices)))
        response = f"**{ctx.author.display_name}'s Updated Hand** (replaced cards {replaced_list}):\n"
        for i, card in enumerate(hand, 1):
            response += f"{i}. {card}\n"
        await ctx.send(response)
    except ValueError:
        await ctx.send(f"{ctx.author.mention}, use numbers 1-6: `$x 1 3 5`")

# ===== HELP COMMAND =====

@bot.command()
async def helpme(ctx):
    """Show all commands"""
    help_text = f"""
**🎴 CARD GAME BOT 🎴**

**DECK MANAGEMENT:**
`{ctx.prefix}cards` - Show your custom deck
`{ctx.prefix}cards @user` - Show another player's deck
`{ctx.prefix}add [card]` - Add a card to your deck
`{ctx.prefix}remove [number]` - Remove a card from your deck
`{ctx.prefix}clear` - Reset your deck to base

**ADMIN COMMANDS:**
`{ctx.prefix}add @user [card]` - Add card to player's deck
`{ctx.prefix}remove @user [number]` - Remove card from player's deck
`{ctx.prefix}clear @user` - Reset player's deck to base

**GAME PLAY:**
`{ctx.prefix}d` - Draw 6 cards from your deck
`{ctx.prefix}x 1 3 5` - Replace cards in your hand
`{ctx.prefix}hand` - Show your current hand
`{ctx.prefix}hand @user` - Show another player's hand
`{ctx.prefix}deck` - Alias for hand

**OTHER FEATURES:**
`roll d20` - Roll a dice
`:sob:` - Get 'L' response

**BASE DECK:** {len(BASE_DECK)} cards
- Elements: Fire, Wind, Water, Earth (3 Mp each)
- Spells: Ball, Bolt (2 Mp), Wall, Burst (3 Mp)
- Moves: Forward, Down (1 Mp), Orbit, Split (2 Mp)

**EXAMPLES:**
1. `{ctx.prefix}add Reverse - cost of what it's reversing`
2. `{ctx.prefix}d` - Draw 6 cards
3. `{ctx.prefix}x 1 4` - Replace cards 1 and 4
4. `{ctx.prefix}hand @John` - See John's hand
5. `{ctx.prefix}cards @Sarah` - See Sarah's deck
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

TOKEN = os.environ.get("DISCCOUNT_TOKEN") or os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    print("❌ ERROR: Set DISCORD_TOKEN environment variable!")
    print("In Railway: Variables → Add DISCORD_TOKEN")
else:
    bot.run(TOKEN)
