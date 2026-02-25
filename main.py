import os
import random
import discord
from discord.ext import commands
import json
from typing import Optional

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

# Player data structure
player_data = {}

def get_player(user_id):
    """Get or create player data"""
    user_id = str(user_id)
    if user_id not in player_data:
        player_data[user_id] = {
            "current_deck": 1,
            "decks": {
                1: {
                    "name": "Deck 1",
                    "cards": BASE_DECK.copy(),
                    "hand_size": 6,
                    "max_mp": 10,
                    "current_mp": 10,
                    "stats": "",
                    "hand": []
                },
                2: {
                    "name": "Deck 2",
                    "cards": [],
                    "hand_size": 6,
                    "max_mp": 10,
                    "current_mp": 10,
                    "stats": "",
                    "hand": []
                },
                3: {
                    "name": "Deck 3",
                    "cards": [],
                    "hand_size": 6,
                    "max_mp": 10,
                    "current_mp": 10,
                    "stats": "",
                    "hand": []
                },
                4: {
                    "name": "Deck 4",
                    "cards": [],
                    "hand_size": 6,
                    "max_mp": 10,
                    "current_mp": 10,
                    "stats": "",
                    "hand": []
                },
                5: {
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
    return player_data[user_id]

def get_current_deck(user_id):
    """Get current deck for a user"""
    player = get_player(user_id)
    deck_num = player["current_deck"]
    return player["decks"][deck_num]

def is_admin(ctx):
    """Check if user is admin"""
    return ctx.author.guild_permissions.administrator

def parse_mention_at_end(args):
    """Parse arguments to check for mention at the end"""
    if not args:
        return None, []
    
    # Check if last arg is a mention
    last_arg = args[-1]
    if len(args) > 1 and last_arg.startswith('<@'):
        # Has mention at the end
        return last_arg, args[:-1]
    return None, args

@bot.event
async def on_ready():
    print(f'✅ Bot ready: {bot.user}')

# ===== DECK MANAGEMENT =====

@bot.command()
async def deck(ctx, deck_num: int, member: Optional[discord.Member] = None):
    """Switch decks: $deck 2 or $deck 3 @player"""
    target = member or ctx.author
    
    if member and not is_admin(ctx):
        await ctx.send("❌ Only admins can switch other players' decks!")
        return
    
    if deck_num < 1 or deck_num > 5:
        await ctx.send("❌ Deck number must be between 1 and 5!")
        return
    
    player = get_player(target.id)
    old_deck = player["current_deck"]
    player["current_deck"] = deck_num
    
    # Reset hand and MP when switching decks
    current = get_current_deck(target.id)
    current["hand"] = []
    current["current_mp"] = current["max_mp"]
    
    if target.id == ctx.author.id:
        await ctx.send(f"✅ Switched from Deck {old_deck} to Deck {deck_num} ({current['name']})")
    else:
        await ctx.send(f"✅ Admin switched {target.display_name} from Deck {old_deck} to Deck {deck_num} ({current['name']})")

@bot.command()
async def name(ctx, *, text: str):
    """Set current deck name: $name My Arena Deck"""
    mention, name_parts = parse_mention_at_end(text.split())
    
    if mention:
        # Admin setting someone else's name
        if not is_admin(ctx):
            await ctx.send("❌ Only admins can set names for other players!")
            return
        
        member = await commands.MemberConverter().convert(ctx, mention)
        deck_name = " ".join(name_parts)
        current = get_current_deck(member.id)
        current["name"] = deck_name
        await ctx.send(f"✅ Set {member.display_name}'s current deck name to: {deck_name}")
    else:
        # Setting own name
        current = get_current_deck(ctx.author.id)
        current["name"] = text
        await ctx.send(f"✅ Set your current deck name to: {text}")

# ===== CARD MANAGEMENT =====

@bot.command()
async def cards(ctx, member: Optional[discord.Member] = None):
    """Show deck cards: $cards or $cards @player"""
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

@bot.command()
async def add(ctx, *, text: str):
    """Add cards: $add Fire - 3 Mp or $add Fire - 3 Mp @player"""
    mention, card_parts = parse_mention_at_end(text.split())
    
    if mention:
        # Admin adding to someone
        if not is_admin(ctx):
            await ctx.send("❌ Only admins can add cards to other players!")
            return
        
        member = await commands.MemberConverter().convert(ctx, mention)
        card_text = " ".join(card_parts)
        current = get_current_deck(member.id)
        current["cards"].append(card_text)
        await ctx.send(f"✅ Admin added to {member.display_name}'s deck: `{card_text}`\nDeck now has {len(current['cards'])} cards.")
    else:
        # Adding to self
        current = get_current_deck(ctx.author.id)
        current["cards"].append(text)
        await ctx.send(f"✅ Added to your deck: `{text}`\nDeck now has {len(current['cards'])} cards.")

@bot.command()
async def remove(ctx, *args):
    """Remove cards: $remove 1 3 5 or $remove 1 3 @player"""
    if not args:
        await ctx.send("Specify cards to remove: `$remove 1 3 5`")
        return
    
    # Check for mention at end
    mention, numbers = parse_mention_at_end(list(args))
    
    if mention:
        # Admin removing from someone
        if not is_admin(ctx):
            await ctx.send("❌ Only admins can remove cards from other players!")
            return
        
        member = await commands.MemberConverter().convert(ctx, mention)
        current = get_current_deck(member.id)
        
        if not current["cards"]:
            await ctx.send(f"{member.display_name}'s deck is empty!")
            return
        
        # Convert to integers and validate
        indices = []
        for num in numbers:
            try:
                idx = int(num)
                if 1 <= idx <= len(current["cards"]):
                    indices.append(idx)
                else:
                    await ctx.send(f"Invalid number: {num} (must be 1-{len(current['cards'])})")
                    return
            except ValueError:
                await ctx.send(f"Invalid number: {num}")
                return
        
        # Remove in reverse order
        removed = []
        for idx in sorted(indices, reverse=True):
            removed.append(current["cards"].pop(idx - 1))
        
        removed_list = ", ".join([f"`{c}`" for c in reversed(removed)])
        await ctx.send(f"✅ Admin removed from {member.display_name}'s deck: {removed_list}\nDeck now has {len(current['cards'])} cards.")
    else:
        # Removing from self
        current = get_current_deck(ctx.author.id)
        
        if not current["cards"]:
            await ctx.send("Your deck is empty!")
            return
        
        # Convert to integers and validate
        indices = []
        for num in args:
            try:
                idx = int(num)
                if 1 <= idx <= len(current["cards"]):
                    indices.append(idx)
                else:
                    await ctx.send(f"Invalid number: {num} (must be 1-{len(current['cards'])})")
                    return
            except ValueError:
                await ctx.send(f"Invalid number: {num}")
                return
        
        # Remove in reverse order
        removed = []
        for idx in sorted(indices, reverse=True):
            removed.append(current["cards"].pop(idx - 1))
        
        removed_list = ", ".join([f"`{c}`" for c in reversed(removed)])
        await ctx.send(f"✅ Removed: {removed_list}\nDeck now has {len(current['cards'])} cards.")

@bot.command()
async def clear(ctx, member: Optional[discord.Member] = None):
    """Clear current deck: $clear or $clear @player"""
    target = member or ctx.author
    
    if member and not is_admin(ctx):
        await ctx.send("❌ Only admins can clear other players' decks!")
        return
    
    current = get_current_deck(target.id)
    current["cards"] = []
    
    if target.id == ctx.author.id:
        await ctx.send(f"✅ Cleared your current deck ({current['name']})")
    else:
        await ctx.send(f"✅ Admin cleared {target.display_name}'s current deck ({current['name']})")

@bot.command()
async def default(ctx, member: Optional[discord.Member] = None):
    """Reset to base deck: $default or $default @player"""
    target = member or ctx.author
    
    if member and not is_admin(ctx):
        await ctx.send("❌ Only admins can reset other players' decks!")
        return
    
    current = get_current_deck(target.id)
    current["cards"] = BASE_DECK.copy()
    
    if target.id == ctx.author.id:
        await ctx.send(f"✅ Reset your current deck ({current['name']}) to base deck ({len(BASE_DECK)} cards)")
    else:
        await ctx.send(f"✅ Admin reset {target.display_name}'s current deck ({current['name']}) to base deck")

# ===== GAME PLAY =====

@bot.command()
async def draw(ctx):
    """Draw a hand: $draw"""
    current = get_current_deck(ctx.author.id)
    
    if len(current["cards"]) < current["hand_size"]:
        await ctx.send(f"❌ You need at least {current['hand_size']} cards in your deck! (You have {len(current['cards'])})")
        return
    
    # Draw hand
    current["hand"] = random.sample(current["cards"], current["hand_size"])
    
    # Show hand with MP
    response = f"**{ctx.author.display_name}'s {current['name']}** - MP: {current['current_mp']}/{current['max_mp']}\n"
    for i, card in enumerate(current["hand"], 1):
        response += f"{i}. {card}\n"
    
    await ctx.send(response)

@bot.command()
async def x(ctx, *card_numbers):
    """Replace cards: $x 1 3 5"""
    current = get_current_deck(ctx.author.id)
    
    if not current["hand"]:
        await ctx.send("Draw a hand first with `$draw`!")
        return
    
    if not card_numbers:
        await ctx.send("Specify cards to replace: `$x 1 3 5`")
        return
    
    hand = current["hand"].copy()
    replaced = []
    
    try:
        for num in card_numbers:
            idx = int(num) - 1
            if 0 <= idx < current["hand_size"]:
                # Replace with random card from deck (not in hand if possible)
                available = [c for c in current["cards"] if c not in hand]
                if available:
                    hand[idx] = random.choice(available)
                else:
                    hand[idx] = random.choice(current["cards"])
                replaced.append(int(num))
        
        current["hand"] = hand
        
        # Show updated hand with MP
        replaced_list = ", ".join(map(str, sorted(replaced)))
        response = f"**{ctx.author.display_name}'s {current['name']}** - MP: {current['current_mp']}/{current['max_mp']} (replaced {replaced_list})\n"
        for i, card in enumerate(hand, 1):
            response += f"{i}. {card}\n"
        
        await ctx.send(response)
    except ValueError:
        await ctx.send(f"Use numbers 1-{current['hand_size']}: `$x 1 3 5`")

@bot.command()
async def hand(ctx, member: Optional[discord.Member] = None):
    """Show current hand: $hand or $hand @player"""
    target = member or ctx.author
    current = get_current_deck(target.id)
    
    if not current["hand"]:
        await ctx.send(f"{target.display_name} hasn't drawn a hand yet!")
        return
    
    response = f"**{target.display_name}'s {current['name']}** - MP: {current['current_mp']}/{current['max_mp']}\n"
    for i, card in enumerate(current["hand"], 1):
        response += f"{i}. {card}\n"
    
    await ctx.send(response)

# ===== MP MANAGEMENT =====

@bot.command()
async def mp(ctx, operation: str, amount: Optional[str] = None, member: Optional[discord.Member] = None):
    """Manage MP: $mp +2, $mp -3, $mp max, or $mp max @player"""
    target = member or ctx.author
    
    if member and not is_admin(ctx):
        await ctx.send("❌ Only admins can modify other players' MP!")
        return
    
    current = get_current_deck(target.id)
    
    # Handle max reset
    if operation.lower() == "max":
        current["current_mp"] = current["max_mp"]
        action = "reset to max"
    elif operation.startswith("+") or operation.startswith("-"):
        try:
            change = int(operation)
            new_mp = current["current_mp"] + change
            # Clamp between 0 and max
            current["current_mp"] = max(0, min(new_mp, current["max_mp"]))
            action = f"{operation} MP"
        except ValueError:
            await ctx.send("Use: `$mp +2`, `$mp -3`, or `$mp max`")
            return
    else:
        await ctx.send("Use: `$mp +2`, `$mp -3`, or `$mp max`")
        return
    
    # Show hand with updated MP
    if current["hand"]:
        response = f"**{target.display_name}'s {current['name']}** - MP: {current['current_mp']}/{current['max_mp']} ({action})\n"
        for i, card in enumerate(current["hand"], 1):
            response += f"{i}. {card}\n"
    else:
        response = f"**{target.display_name}'s {current['name']}** - MP: {current['current_mp']}/{current['max_mp']} ({action})\nNo hand drawn yet."
    
    await ctx.send(response)

# ===== SETTINGS =====

@bot.command()
async def settings(ctx, setting: Optional[str] = None, value: Optional[str] = None, member: Optional[discord.Member] = None):
    """View or change settings: $settings, $settings hand 8, $settings mp 15 @player"""
    
    # Just view settings
    if setting is None:
        current = get_current_deck(ctx.author.id)
        response = f"**{ctx.author.display_name}'s {current['name']} Settings:**\n"
        response += f"• Hand Size: {current['hand_size']}\n"
        response += f"• Max MP: {current['max_mp']}\n"
        response += f"• Current MP: {current['current_mp']}/{current['max_mp']}\n"
        response += f"• Cards in Deck: {len(current['cards'])}\n"
        if current["stats"]:
            response += f"• Stats: {current['stats']}"
        await ctx.send(response)
        return
    
    # Changing settings
    target = member or ctx.author
    
    if member and not is_admin(ctx):
        await ctx.send("❌ Only admins can change settings for other players!")
        return
    
    if value is None:
        await ctx.send(f"Specify a value: `$settings {setting} 8`")
        return
    
    current = get_current_deck(target.id)
    
    try:
        if setting.lower() == "hand":
            new_value = int(value)
            if new_value < 1 or new_value > 20:
                await ctx.send("Hand size must be between 1 and 20!")
                return
            current["hand_size"] = new_value
            await ctx.send(f"✅ Set {target.display_name}'s hand size to {new_value}")
            
        elif setting.lower() == "mp":
            new_value = int(value)
            if new_value < 1 or new_value > 100:
                await ctx.send("Max MP must be between 1 and 100!")
                return
            current["max_mp"] = new_value
            current["current_mp"] = new_value  # Reset to new max
            await ctx.send(f"✅ Set {target.display_name}'s max MP to {new_value}")
            
        else:
            await ctx.send("Invalid setting! Use `hand` or `mp`")
            
    except ValueError:
        await ctx.send("Value must be a number!")

# ===== STATS =====

@bot.command()
async def stats(ctx, *, text: Optional[str] = None):
    """View or set stats: $stats or $stats My arena stats"""
    if text is None:
        # View stats
        current = get_current_deck(ctx.author.id)
        if current["stats"]:
            await ctx.send(f"**{ctx.author.display_name}'s {current['name']} Stats:**\n{current['stats']}")
        else:
            await ctx.send(f"No stats set for {ctx.author.display_name}'s {current['name']}. Use `$stats your text here` to set them.")
        return
    
    # Check for mention at end for admin setting
    mention, stat_parts = parse_mention_at_end(text.split())
    
    if mention:
        # Admin setting stats for someone
        if not is_admin(ctx):
            await ctx.send("❌ Only admins can set stats for other players!")
            return
        
        member = await commands.MemberConverter().convert(ctx, mention)
        stat_text = " ".join(stat_parts)
        current = get_current_deck(member.id)
        current["stats"] = stat_text
        await ctx.send(f"✅ Set stats for {member.display_name}'s {current['name']}")
    else:
        # Setting own stats
        current = get_current_deck(ctx.author.id)
        current["stats"] = text
        await ctx.send(f"✅ Set stats for your {current['name']}")

# ===== ROLL =====

@bot.command()
async def r(ctx):
    """Roll d20: $r"""
    r = random.randint(1, 20)
    if r == 1:
        response = f'🎲 Rolled **{r}** - Critical fail!'
    elif r == 20:
        response = f'🎲 Rolled **{r}** - NATURAL 20! 🎉'
    elif r < 10:
        response = f'🎲 Rolled **{r}** - get fucked lmao!'
    else:
        response = f'🎲 Rolled **{r}** - not bad!'
    await ctx.send(response)

# ===== SOB REACTION =====

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if ":sob:" in message.content:
        await message.channel.send("L")
    
    await bot.process_commands(message)

# ===== HELP =====

@bot.command()
async def helpme(ctx):
    """Show all commands"""
    help_text = f"""
**🎴 MYTHOS BOT, SLAYER OF TREYS - COMPLETE COMMANDS 🎴**

**DECK MANAGEMENT:**
`$cards` - Show your current deck
`$cards @player` - Show another player's deck (admin)
`$add [card]` - Add card to your deck
`$add [card] @player` - Add card to player's deck (admin)
`$remove 1 3 5` - Remove multiple cards
`$remove 1 3 @player` - Remove from player's deck (admin)
`$clear` - Clear your current deck
`$clear @player` - Clear player's deck (admin)
`$default` - Reset to base 12 cards
`$default @player` - Reset player's deck (admin)

**DECK SWITCHING:**
`$deck 2` - Switch to deck 2
`$deck 3 @player` - Switch player's deck (admin)
`$name My Deck` - Name your current deck
`$name Arena @player` - Name player's deck (admin)

**GAME PLAY:**
`$draw` - Draw a hand
`$hand` - Show your current hand
`$hand @player` - Show player's hand
`$x 1 3 5` - Replace cards in hand

**MP SYSTEM:**
`$mp +2` - Add MP
`$mp -3` - Subtract MP
`$mp max` - Reset to max MP
`$mp max @player` - Reset player's MP (admin)

**SETTINGS:**
`$settings` - View current settings
`$settings hand 8` - Set hand size
`$settings hand 8 @player` - Set player's hand size (admin)
`$settings mp 15` - Set max MP
`$settings mp 15 @player` - Set player's max MP (admin)

**STATS:**
`$stats` - View stats
`$stats My arena stats` - Set your stats
`$stats New stats @player` - Set player's stats (admin)

**OTHER:**
`$r` - Roll d20
`$helpme` - This message

**DEFAULTS:**
• 5 decks per player (Deck 1 has base cards, others empty)
• Hand size: 6 | Max MP: 10
• Base deck: {len(BASE_DECK)} cards
"""
    await ctx.send(help_text)

# ===== RUN BOT =====

TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    print("❌ ERROR: Set DISCORD_TOKEN environment variable!")
    print("In Railway: Variables → Add DISCORD_TOKEN")
else:
    bot.run(TOKEN)
