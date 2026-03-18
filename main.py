import os
import random
import discord
from discord.ext import commands
from typing import Optional
import json
import asyncio

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
        save_data()
    return player_data[user_id]

def get_current_deck(user_id):
    """Get current deck for a user"""
    player = get_player(user_id)
    deck_num = player["current_deck"]
    return player["decks"][str(deck_num)]

def is_admin(ctx):
    """Check if user is admin"""
    return ctx.author.guild_permissions.administrator

@bot.event
async def on_ready():
    load_data()
    print(f'✅ Bot ready: {bot.user}')

# ===== DECK MANAGEMENT =====

@bot.command()
async def deck(ctx, action: str, member: Optional[discord.Member] = None):
    """Switch or reset decks: $deck 2, $deck 3 @player, or $deck reset"""
    if action.lower() == "reset":
        target = member or ctx.author
        
        if member and not is_admin(ctx):
            await ctx.send("❌ Only admins can reset other players' decks!")
            return
        
        player = get_player(target.id)
        deck_num = player["current_deck"]
        deck = player["decks"][str(deck_num)]
        
        # Reset deck to defaults
        deck["name"] = f"Deck {deck_num}"
        deck["cards"] = [] if deck_num != 1 else BASE_DECK.copy()
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
    player["current_deck"] = deck_num
    
    # Reset hand and MP when switching decks
    current = get_current_deck(target.id)
    current["hand"] = []
    current["current_mp"] = current["max_mp"]
    
    save_data()
    
    if target.id == ctx.author.id:
        await ctx.send(f"✅ Switched from Deck {old_deck} to Deck {deck_num} ({current['name']})")
    else:
        await ctx.send(f"✅ Admin switched {target.display_name} from Deck {old_deck} to Deck {deck_num} ({current['name']})")

@bot.command()
async def decks(ctx, member: Optional[discord.Member] = None):
    """Show list of decks with preview: $decks or $decks @player"""
    target = member or ctx.author
    player = get_player(target.id)
    
    response = f"**{target.display_name}'s Decks:**\n"
    
    for deck_num in range(1, 6):
        deck = player["decks"][str(deck_num)]
        current_marker = "✅ " if player["current_deck"] == deck_num else ""
        response += f"\n{current_marker}**Deck {deck_num}: {deck['name']}** ({len(deck['cards'])} cards)\n"
        
        # Show preview of first 3 cards
        if deck["cards"]:
            preview = ", ".join([f"`{c[:20]}...`" if len(c) > 20 else f"`{c}`" for c in deck["cards"][:3]])
            if len(deck["cards"]) > 3:
                preview += f" and {len(deck['cards']) - 3} more"
            response += f"Preview: {preview}\n"
        else:
            response += "Preview: *Empty deck*\n"
    
    # Handle long messages
    if len(response) > 2000:
        # Split into multiple messages
        parts = [response[i:i+1900] for i in range(0, len(response), 1900)]
        for i, part in enumerate(parts, 1):
            await ctx.send(f"**Part {i}:**\n{part}")
    else:
        await ctx.send(response)

@bot.command()
async def name(ctx, *, text: str):
    """Set current deck name: $name My Arena Deck"""
    # Check for mention at the end
    parts = text.strip().split()
    if parts and parts[-1].startswith('<@') and parts[-1].endswith('>'):
        mention = parts[-1]
        deck_name = " ".join(parts[:-1])
        
        if not is_admin(ctx):
            await ctx.send("❌ Only admins can set names for other players!")
            return
        
        try:
            member = await commands.MemberConverter().convert(ctx, mention)
        except:
            await ctx.send("Invalid user mention!")
            return
        
        if not deck_name:
            await ctx.send("Please provide a name!")
            return
        
        current = get_current_deck(member.id)
        current["name"] = deck_name
        save_data()
        await ctx.send(f"✅ Set {member.display_name}'s current deck name to: {deck_name}")
    
    else:
        # Setting own name
        if not text:
            await ctx.send("Please provide a name!")
            return
        
        current = get_current_deck(ctx.author.id)
        current["name"] = text
        save_data()
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
    """Add cards: $add Fire - 3 Mp (one per line for multiple)"""
    
    # Check if this is a bulk add (contains line breaks)
    if '\n' in text:
        # Split by lines and clean up
        lines = text.strip().split('\n')
        cards_to_add = []
        mention = None
        
        for line in lines:
            line = line.strip()
            if not line:  # Skip empty lines
                continue
            
            # Check if this line is a mention
            if line.startswith('<@') and line.endswith('>'):
                mention = line
            else:
                cards_to_add.append(line)
        
        if not cards_to_add:
            await ctx.send("No valid cards found to add!")
            return
        
        # Handle mention (admin adding to someone)
        if mention:
            if not is_admin(ctx):
                await ctx.send("❌ Only admins can add cards to other players!")
                return
            
            try:
                member = await commands.MemberConverter().convert(ctx, mention)
            except:
                await ctx.send("Invalid user mention!")
                return
            
            current = get_current_deck(member.id)
            added_count = 0
            for card in cards_to_add:
                current["cards"].append(card)
                added_count += 1
            
            save_data()
            
            preview = ", ".join([f"`{c[:20]}...`" if len(c) > 20 else f"`{c}`" for c in cards_to_add[:3]])
            if added_count > 3:
                preview += f" and {added_count - 3} more"
            
            await ctx.send(f"✅ Admin added {added_count} card(s) to {member.display_name}'s deck\n{preview}\nDeck now has {len(current['cards'])} cards.")
            return
        
        # Adding to self (multiple cards)
        current = get_current_deck(ctx.author.id)
        added_count = 0
        for card in cards_to_add:
            current["cards"].append(card)
            added_count += 1
        
        save_data()
        
        preview = ", ".join([f"`{c[:20]}...`" if len(c) > 20 else f"`{c}`" for c in cards_to_add[:3]])
        if added_count > 3:
            preview += f" and {added_count - 3} more"
        
        await ctx.send(f"✅ Added {added_count} card(s) to your deck\n{preview}\nDeck now has {len(current['cards'])} cards.")
    
    else:
        # Single card add (no line breaks)
        # Check for mention at the end
        parts = text.strip().split()
        if parts and parts[-1].startswith('<@') and parts[-1].endswith('>'):
            mention = parts[-1]
            card_text = " ".join(parts[:-1])
            
            if not is_admin(ctx):
                await ctx.send("❌ Only admins can add cards to other players!")
                return
            
            try:
                member = await commands.MemberConverter().convert(ctx, mention)
            except:
                await ctx.send("Invalid user mention!")
                return
            
            current = get_current_deck(member.id)
            current["cards"].append(card_text)
            save_data()
            await ctx.send(f"✅ Admin added to {member.display_name}'s deck: `{card_text}`\nDeck now has {len(current['cards'])} cards.")
        
        else:
            # Adding single card to self
            current = get_current_deck(ctx.author.id)
            current["cards"].append(text)
            save_data()
            await ctx.send(f"✅ Added to your deck: `{text}`\nDeck now has {len(current['cards'])} cards.")

@bot.command()
async def remove(ctx, *args):
    """Remove cards: $remove 1 3 5 or $remove 1 3 @player"""
    if not args:
        await ctx.send("Specify cards to remove: `$remove 1 3 5`")
        return
    
    # Check for mention at the end
    args_list = list(args)
    if args_list and args_list[-1].startswith('<@') and args_list[-1].endswith('>'):
        mention = args_list[-1]
        numbers = args_list[:-1]
        
        # Admin removing from someone
        if not is_admin(ctx):
            await ctx.send("❌ Only admins can remove cards from other players!")
            return
        
        try:
            member = await commands.MemberConverter().convert(ctx, mention)
        except:
            await ctx.send("Invalid user mention!")
            return
        
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
        
        save_data()
        
        removed_list = ", ".join([f"`{c}`" for c in reversed(removed)])
        await ctx.send(f"✅ Admin removed from {member.display_name}'s deck: {removed_list}\nDeck now has {len(current['cards'])} cards.")
    
    else:
        # Removing from self
        current = get_current_deck(ctx.author.id)
        numbers = args  # args are already the numbers
        
        if not current["cards"]:
            await ctx.send("Your deck is empty!")
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
        
        save_data()
        
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
    save_data()
    
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
    save_data()
    
    if target.id == ctx.author.id:
        await ctx.send(f"✅ Reset your current deck ({current['name']}) to base deck ({len(BASE_DECK)} cards)")
    else:
        await ctx.send(f"✅ Admin reset {target.display_name}'s current deck ({current['name']}) to base deck")

# ===== GAME PLAY =====

@bot.command()
async def draw(ctx, member: Optional[discord.Member] = None):
    """Draw a hand: $draw or $draw @player (admin only for others)"""
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

@bot.command()
async def x(ctx, *args):
    """Replace cards: $x 1 3 5 or $x 1 3 5 @player (admin only for others)"""
    if not args:
        await ctx.send("Specify cards to replace: `$x 1 3 5`")
        return
    
    # Check for mention at the end
    args_list = list(args)
    if args_list and args_list[-1].startswith('<@') and args_list[-1].endswith('>'):
        mention = args_list[-1]
        card_numbers = args_list[:-1]
        target_mention = True
    else:
        mention = None
        card_numbers = args_list
        target_mention = False
    
    if target_mention:
        if not is_admin(ctx):
            await ctx.send("❌ Only admins can replace cards for other players!")
            return
        
        try:
            member = await commands.MemberConverter().convert(ctx, mention)
        except:
            await ctx.send("Invalid user mention!")
            return
        
        target = member
    else:
        target = ctx.author
    
    current = get_current_deck(target.id)
    
    if not current["hand"]:
        await ctx.send(f"{target.display_name} hasn't drawn a hand yet!")
        return
    
    if not card_numbers:
        await ctx.send("Specify cards to replace!")
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
        save_data()
        
        # Show updated hand with MP
        replaced_list = ", ".join(map(str, sorted(replaced)))
        
        if target_mention:
            response = f"**{target.display_name}'s {current['name']}** - MP: {current['current_mp']}/{current['max_mp']} (Admin replaced {replaced_list})\n"
        else:
            response = f"**{target.display_name}'s {current['name']}** - MP: {current['current_mp']}/{current['max_mp']} (replaced {replaced_list})\n"
        
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
async def mp(ctx, operation: str, member: Optional[discord.Member] = None):
    """Manage MP: $mp +2, $mp -3, $mp max, or $mp max @player (MP can go negative)"""
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
            # Allow negative MP (no lower bound)
            current["current_mp"] += change
            action = f"{operation} MP"
        except ValueError:
            await ctx.send("Use: `$mp +2`, `$mp -3`, or `$mp max`")
            return
    else:
        await ctx.send("Use: `$mp +2`, `$mp -3`, or `$mp max`")
        return
    
    save_data()
    
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
            save_data()
            await ctx.send(f"✅ Set {target.display_name}'s hand size to {new_value}")
            
        elif setting.lower() == "mp":
            new_value = int(value)
            if new_value < 1 or new_value > 100:
                await ctx.send("Max MP must be between 1 and 100!")
                return
            current["max_mp"] = new_value
            current["current_mp"] = new_value  # Reset to new max
            save_data()
            await ctx.send(f"✅ Set {target.display_name}'s max MP to {new_value}")
            
        else:
            await ctx.send("Invalid setting! Use `hand` or `mp`")
            
    except ValueError:
        await ctx.send("Value must be a number!")

# ===== STATS =====

@bot.command()
async def stats(ctx, *, text: Optional[str] = None):
    """View or set stats: $stats, $stats My arena stats, or $stats New stats @player"""
    if text is None:
        # View stats
        current = get_current_deck(ctx.author.id)
        if current["stats"]:
            await ctx.send(f"**{ctx.author.display_name}'s {current['name']} Stats:**\n{current['stats']}")
        else:
            await ctx.send(f"No stats set for {ctx.author.display_name}'s {current['name']}. Use `$stats your text here` to set them.")
        return
    
    # Check for mention at the end
    parts = text.strip().split()
    if parts and parts[-1].startswith('<@') and parts[-1].endswith('>'):
        mention = parts[-1]
        stat_text = " ".join(parts[:-1])
        
        if not is_admin(ctx):
            await ctx.send("❌ Only admins can set stats for other players!")
            return
        
        try:
            member = await commands.MemberConverter().convert(ctx, mention)
        except:
            await ctx.send("Invalid user mention!")
            return
        
        if not stat_text:
            await ctx.send("Please provide stats text!")
            return
        
        current = get_current_deck(member.id)
        current["stats"] = stat_text
        save_data()
        await ctx.send(f"✅ Set stats for {member.display_name}'s {current['name']}")
    
    else:
        # Setting own stats
        if not text:
            await ctx.send("Please provide stats text!")
            return
        
        current = get_current_deck(ctx.author.id)
        current["stats"] = text
        save_data()
        await ctx.send(f"✅ Set stats for your {current['name']}")

# ===== ROLL =====

@bot.command()
async def r(ctx):
    """Roll d20: $r"""
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

# ===== HELP =====

@bot.command()
async def helpme(ctx):
    """Show all commands"""
    help_text = f"""
**🎴 CARD GAME BOT - COMPLETE COMMANDS 🎴**

**DECK MANAGEMENT:**
`$cards` - Show your current deck
`$cards @player` - Show another player's deck (admin)
`$add [card]` - Add card(s) to your deck (one per line)
`$add [card] @player` - Add to player's deck (admin)
`$remove 1 3 5` - Remove multiple cards
`$remove 1 3 @player` - Remove from player's deck (admin)
`$clear` - Clear your current deck
`$clear @player` - Clear player's deck (admin)
`$default` - Reset to base 12 cards
`$default @player` - Reset player's deck (admin)

**DECK SWITCHING:**
`$deck 2` - Switch to deck 2
`$deck 3 @player` - Switch player's deck (admin)
`$deck reset` - Reset current deck to defaults
`$deck reset @player` - Reset player's deck (admin)
`$decks` - Show all decks with preview
`$decks @player` - Show player's decks (admin)
`$name My Deck` - Name your current deck
`$name Arena @player` - Name player's deck (admin)

**GAME PLAY:**
`$draw` - Draw a hand
`$draw @player` - Draw for player (admin)
`$hand` - Show your current hand
`$hand @player` - Show player's hand
`$x 1 3 5` - Replace cards in hand
`$x 1 3 5 @player` - Replace player's cards (admin)

**MP SYSTEM:**
`$mp +2` - Add MP (can go negative)
`$mp -3` - Subtract MP (can go negative)
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
• Hand size: 6 | Max MP: 10 (can go negative)
• Base deck: {len(BASE_DECK)} cards
• Data auto-saves to file

**BULK ADD EXAMPLE:**
$add
Fire - 3 Mp
Wind - 3 Mp
Water - 3 Mp
Earth - 3 Mp

"""
    await ctx.send(help_text)

# ===== RUN BOT =====

TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    print("❌ ERROR: Set DISCORD_TOKEN environment variable!")
    print("In Railway: Variables → Add DISCORD_TOKEN")
else:
    bot.run(TOKEN)
