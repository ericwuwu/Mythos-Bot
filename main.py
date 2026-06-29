import os
import discord
import random
import json
import sys

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Define the complete library of cards
card_library = {
    1: {"name": "Fire", "mp": 3, "type": "Element", "info": "creates flames using mana"},
    2: {"name": "Wind", "mp": 3, "type": "Element", "info": "creates wind using mana"},
    3: {"name": "Water", "mp": 3, "type": "Element", "info": "creates water using mana"},
    4: {"name": "Earth", "mp": 3, "type": "Element", "info": "creates earth using mana"},
    5: {"name": "Null", "mp": 1, "type": "Element", "info": "solidifies pure mana, able to take on aspects of elements it comes in contact with"},
    6: {"name": "Dark", "mp": 4, "type": "Element", "info": "creates darkness using mana, weak physically unless condensed"},
    7: {"name": "Light", "mp": 4, "type": "Element", "info": "creates light using mana, weak physically unless condensed"},
    8: {"name": "Magma", "mp": 5, "type": "Element", "info": "creates magma, a fusion of <Fire> and <Earth> using mana"},
    9: {"name": "Lightning", "mp": 6, "type": "Element", "info": "creates lightning using mana, advanced form of <Fire> that strikes with clusters of electricity"},
    10: {"name": "Ice", "mp": 5, "type": "Element", "info": "creates ice using mana, advanced form of <Water> that spreads its frozen touch"},
    11: {"name": "Storm", "mp": 6, "type": "Element", "info": "creates miniature storms using mana, a fusion of <Wind> and <Water> (if condensed, chance of electricity generated is increased)"},
    12: {"name": "Sound", "mp": 5, "type": "Element", "info": "creates sound using mana, advanced form of <Wind> that uses precise manipulation and could create shockwaves"},
    13: {"name": "Vacuum", "mp": 6, "type": "Element", "info": "creates a vacuum using mana, advanced form of <Wind> that sucks out the very matter from a area"},
    14: {"name": "Metal", "mp": 5, "type": "Element", "info": "creates metal using mana, advanced form of <Earth> that forms reinforced alloy several times stronger than stone (its traits can vary)"},
    15: {"name": "Gravity", "mp": 6, "type": "Element", "info": "creates a gravity field using mana, advanced form of <Earth> that warps space towards a direction"},
    16: {"name": "Demonic", "mp": 6, "type": "Element", "info": "summons demonic energy using mana, eats away at the one's flesh using their sins and leaving the wound difficult to heal (optional targeting)"},
    17: {"name": "Divine", "mp": 6, "type": "Element", "info": "summons divine energy using mana, judges targets for their sins and mends the wounds of allies (optional targeting)"},
    18: {"name": "Hellfire", "mp": 8, "type": "Element", "info": "creates hellfire using mana, a fusion of <Fire> and <Divine> that passes judgement on a target, burning for as long as their sins can fuel it (optional targeting, can heal allies)"},
    19: {"name": "Permafrost", "mp": 8, "type": "Element", "info": "creates permafrost using mana, a fusion of <Ice> and <Demonic> that corrodes one's skin, freezing it for as long as their sins can fuel it (optional targeting, hard to heal)"},
    20: {"name": "Void", "mp": 10, "type": "Element", "info": "creates a void, a tear in space using mana that rips apart anything it touches, its sheer power makes it difficult to manipulate as a element, causing elements, shapes, and trajectories added to be double cost (the void is slow moving but overwhelmingly powerful)"},
    21: {"name": "Ball", "mp": 2, "type": "Shape", "info": "condenses the element into a ball, rupturing when broken"},
    22: {"name": "Bolt", "mp": 2, "type": "Shape", "info": "condenses the element into a javelin, piercing those in its path"},
    23: {"name": "Wall", "mp": 3, "type": "Shape", "info": "condenses the element into a wall about 6 by 6 ft in length (able to be slightly changed)"},
    24: {"name": "Burst", "mp": 3, "type": "Shape", "info": "condenses the element that then explodes out in every direction with great force"},
    25: {"name": "Slash", "mp": 2, "type": "Shape", "info": "condenses the element into a crescent shape able to cut through those in its way"},
    26: {"name": "Pillar", "mp": 4, "type": "Shape", "info": "shoots out a element in a circular beam several feet wide from the ground/sky in a vertical direction for several seconds"},
    27: {"name": "Swamp", "mp": 5, "type": "Shape", "info": "spreads the element on the ground in a 10 feet diameter"},
    28: {"name": "Beam", "mp": 4, "type": "Shape", "info": "shoots out a element in a small circular beam like a laser for several seconds"},
    29: {"name": "Wire", "mp": 2, "type": "Shape", "info": "condenses the element into a single sharp thread, its length variable"},
    30: {"name": "Trail", "mp": 2, "type": "Shape", "info": "leaves a trail of a element as the spells move, the lingering effect is a weaker version of said element"},
    31: {"name": "Forward", "mp": 1, "type": "Command", "info": "propels a spell forward, its direction is varying"},
    32: {"name": "Down", "mp": 1, "type": "Command", "info": "slams the spell downwards quickly"},
    33: {"name": "Spin", "mp": 2, "type": "Command", "info": "spins the entire or parts of the spell around"},
    34: {"name": "Split", "mp": 2, "type": "Command", "info": "splits a spell into smaller versions, number of splits varying"},
    35: {"name": "Reverse", "mp": "Variable", "type": "Command", "info": "reverses the trajectory that went before it"},
    36: {"name": "Chain", "mp": 3, "type": "Command", "info": "chain the spell's effect from one target to another near each other"},
    37: {"name": "Trap", "mp": 4, "type": "Command", "info": "places a spell on the ground that is activated when something is over its surface"},
    38: {"name": "Arc", "mp": 2, "type": "Command", "info": "propels a spell forward in a arc, its direction varying"},
    39: {"name": "Expand", "mp": "Variable", "type": "Command", "info": "doubles the size of a spell, costing x2 more Mp each size double"},
    40: {"name": "Shrink", "mp": "Variable", "type": "Command", "info": "halves the size of a spell, costing x2 more Mp each size is halved"},
    41: {"name": "Drill", "mp": 4, "type": "Command", "info": "propel a spell forward in a arc, piercing through environments in its way"},
    42: {"name": "Turn", "mp": 1, "type": "Command", "info": "a weaker <forward> used to make a spell redirect towards the target"},
    43: {"name": "Homing", "mp": 3, "type": "Command", "info": "curves the spell towards a target slightly"},
    44: {"name": "Ripple", "mp": 5, "type": "Command", "info": "sends out a spell in a 360 wave that ripples outward, fast at first but slows as it goes further (stops at environments blocking its way)"},
    45: {"name": "Delay", "mp": 1, "type": "Command", "info": "delays the next cards in sequence for a spell, time delayed varying"},
    46: {"name": "Curse", "mp": 5, "type": "Command", "info": "curses the target based on how much the spell hits them and activates the next spell"},
    47: {"name": "Soften", "mp": "Variable", "type": "Command", "info": "softens the spell or spell shape, intensity based on amount of mp used"},
    48: {"name": "Harden", "mp": "Variable", "type": "Command", "info": "hardens the spell or spell shape, intensity based on amount of mp used"},
    49: {"name": "External", "mp": 3, "type": "Command", "info": "gathers the element specified and allows the user to manipulate it with spell cards"},
    50: {"name": "Memory", "mp": "Variable", "type": "Command", "info": "copies cards used recently, the cards costing the mirrored cards' total mp +1 mp per card"}
}

# Data structure for each user
user_data = {}

# File to save data
DATA_FILE = "user_data.json"

def load_data():
    global user_data
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                user_data = json.load(f)
                print("Data loaded successfully!")
        else:
            print("No save file found, starting fresh.")
    except Exception as e:
        print(f"Error loading data: {e}")
        user_data = {}

def save_data():
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(user_data, f, indent=4)
            print("Data saved successfully!")
    except Exception as e:
        print(f"Error saving data: {e}")

def get_user(user_id):
    user_id = str(user_id)
    if user_id not in user_data:
        user_data[user_id] = {
            "mp": 0,
            "mp_recovery": 4,
            "mp_cap": 0,
            "inventory": {},
            "active_deck": [],
            "deck_mode": "limitless",
            "hand": [],
            "bad_luck_streak": 0,
            "good_luck_streak": 0
        }
        save_data()
    return user_data[user_id]

def format_card(card_num):
    card = card_library[card_num]
    if card["mp"] == "Variable":
        return f"{card['name']} - Variable Mp ({card['type']})"
    return f"{card['name']} - {card['mp']} Mp ({card['type']})"

def format_hand(hand):
    if not hand:
        return "No cards in hand."
    result = ""
    for i, card_num in enumerate(hand, 1):
        result += f"{i}. {format_card(card_num)}\n"
    return result

def format_active_deck(deck):
    if not deck:
        return "Empty"
    result = ""
    for i, card_num in enumerate(deck, 1):
        result += f"{i}. {format_card(card_num)}\n"
    return result

def format_inventory(inventory):
    if not inventory:
        return "Empty"
    result = ""
    for card_num, quantity in inventory.items():
        card_num = int(card_num)
        if card_num in card_library:
            card = card_library[card_num]
            result += f"{card_num}. {card['name']} - {quantity}x\n"
    return result

def smart_d20_roll(user_id):
    user = get_user(user_id)
    bad_streak = user["bad_luck_streak"]
    good_streak = user["good_luck_streak"]
    
    # Base roll
    roll = random.randint(1, 20)
    
    # Apply bad luck streak modifier (makes low rolls rarer)
    if bad_streak > 0 and roll <= 5:
        # Reduced chance of low rolls
        if bad_streak >= 5:
            reduction = 0.8
        else:
            reduction = bad_streak * 0.15  # 15% per streak up to 75%
        
        # Try to reroll if we hit a low number
        if random.random() < reduction:
            # Reroll with higher numbers weighted
            roll = random.randint(5 + bad_streak, 20)
    
    # Apply good luck streak modifier (makes high rolls rarer after too many good rolls)
    if good_streak > 0:
        # After 2 good rolls, start making bad rolls more likely
        if good_streak >= 2:
            # Calculate bonus chance for bad rolls
            bad_bonus = 0.1  # 10% base
            
            # If roll was high, increase the bonus
            if roll >= 10:
                bad_bonus *= 1.5
            if roll >= 15:
                bad_bonus *= 2.0
            
            # Chance to reduce the roll
            if random.random() < bad_bonus:
                # Reduce the roll by a random amount
                reduction_amount = random.randint(1, min(10, good_streak * 2))
                roll = max(1, roll - reduction_amount)
    
    # Update streaks based on roll
    if roll <= 5:
        user["bad_luck_streak"] += 1
        user["good_luck_streak"] = max(0, user["good_luck_streak"] - 1)
    elif roll >= 16:
        user["good_luck_streak"] += 1
        user["bad_luck_streak"] = max(0, user["bad_luck_streak"] - 1)
    else:
        # Middle rolls gradually reduce streaks
        user["bad_luck_streak"] = max(0, user["bad_luck_streak"] - 0.5)
        user["good_luck_streak"] = max(0, user["good_luck_streak"] - 0.5)
    
    # Cap streaks
    user["bad_luck_streak"] = min(10, int(user["bad_luck_streak"]))
    user["good_luck_streak"] = min(10, int(user["good_luck_streak"]))
    
    save_data()
    return roll

def ensure_category_balance(hand):
    """Ensure hand has at least one of each category (Element, Shape, Command)"""
    categories = {"Element": 0, "Shape": 0, "Command": 0}
    
    # Count current categories
    for card_num in hand:
        if card_num in card_library:
            card_type = card_library[card_num]["type"]
            if card_type in categories:
                categories[card_type] += 1
    
    # Check which categories are missing
    missing_categories = [cat for cat, count in categories.items() if count == 0]
    
    if not missing_categories:
        return hand  # All categories present
    
    # Replace duplicate categories with missing ones
    new_hand = hand.copy()
    category_counts = {"Element": 0, "Shape": 0, "Command": 0}
    
    # Count categories in current hand
    for card_num in new_hand:
        if card_num in card_library:
            card_type = card_library[card_num]["type"]
            if card_type in category_counts:
                category_counts[card_type] += 1
    
    # Find cards to replace (from categories with counts > 1)
    for i, card_num in enumerate(new_hand):
        if card_num in card_library:
            card_type = card_library[card_num]["type"]
            if category_counts.get(card_type, 0) > 1:
                # This category has duplicates, can replace one
                for missing_cat in missing_categories:
                    # Find a card of the missing category
                    possible_cards = [num for num, card in card_library.items() 
                                    if card["type"] == missing_cat and num not in new_hand]
                    if possible_cards:
                        new_hand[i] = random.choice(possible_cards)
                        category_counts[card_type] -= 1
                        category_counts[missing_cat] = category_counts.get(missing_cat, 0) + 1
                        missing_categories.remove(missing_cat)
                        break
        if not missing_categories:
            break
    
    return new_hand

@client.event
async def on_ready():
    load_data()
    print(f'We have logged in as {client.user}')
    print(f'Bot is in {len(client.guilds)} guilds')
    print('Bot is ready!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content
    user_id = str(message.author.id)
    user = get_user(user_id)
    
    # HELP COMMAND
    if content.startswith('$help'):
        help_text = """
**Available Commands:**
`$library all/element/shape/command` - View cards by category
`$info #` - Get card details
`$add` (two lines: card_number quantity) - Add cards to inventory
`$cards` - Check full inventory
`$use # # #` - Put cards into active deck (takes from inventory)
`$deck` - Show current active deck
`$plus #` - Add card to active deck (even after draw)
`$draw` - Draw 6 cards from active deck (clears after)
`$num # +/-#` - Modify card quantities
`$num random #/all` - Randomize quantities
`$mp turn` - Add MP recovery
`$settings turn #` - Set MP recovery
`$settings deck # limited/limitless` - Set deck mode
`$reset all` - Full reset for everyone
`$x #` - Reroll cards (with category protection)
`$r` - Roll d20 with smart RNG
`$hand` - Show current hand
        """
        await message.channel.send(help_text)
        return

    # LIBRARY COMMAND
    if content.startswith('$library'):
        parts = content.split()
        category = parts[1] if len(parts) > 1 else "all"
        
        result = "**Card Library:**\n"
        if category == "all":
            for num, card in card_library.items():
                if card["mp"] == "Variable":
                    result += f"{num}. {card['name']} - Variable Mp ({card['type']})\n"
                else:
                    result += f"{num}. {card['name']} - {card['mp']} Mp ({card['type']})\n"
        else:
            # Filter by category
            category_map = {"element": "Element", "shape": "Shape", "command": "Command"}
            cat_filter = category_map.get(category.lower(), category.capitalize())
            
            for num, card in card_library.items():
                if card["type"] == cat_filter:
                    if card["mp"] == "Variable":
                        result += f"{num}. {card['name']} - Variable Mp ({card['type']})\n"
                    else:
                        result += f"{num}. {card['name']} - {card['mp']} Mp ({card['type']})\n"
        
        await message.channel.send(result[:2000])  # Discord message limit
        return

    # INFO COMMAND
    if content.startswith('$info'):
        parts = content.split()
        if len(parts) < 2:
            await message.channel.send("Please specify a card number. Example: `$info 1`")
            return
        
        try:
            card_num = int(parts[1])
            if card_num not in card_library:
                await message.channel.send(f"Card #{card_num} not found in library.")
                return
            
            card = card_library[card_num]
            info_text = f"""
**Card #{card_num}: {card['name']}**
Type: {card['type']}
MP Cost: {card['mp']} Mp
Info: {card['info']}
            """
            await message.channel.send(info_text)
        except ValueError:
            await message.channel.send("Please provide a valid number.")
        return

    # ADD COMMAND - Two line format
    if content.startswith('$add'):
        # Wait for the next message with the numbers
        await message.channel.send("Please enter the card numbers and quantities (one per line):\nExample:\n`1 2`\n`2 3`")
        
        def check(m):
            return m.author == message.author and m.channel == message.channel
        
        try:
            # Get the next message
            msg = await client.wait_for('message', timeout=60.0, check=check)
            lines = msg.content.strip().split('\n')
            
            added_cards = []
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 2:
                    try:
                        card_num = int(parts[0])
                        quantity = int(parts[1])
                        
                        if card_num not in card_library:
                            await message.channel.send(f"Card #{card_num} not found in library.")
                            continue
                        
                        # Add to inventory
                        if user["deck_mode"] == "limited":
                            # In limited mode, each card starts with 5
                            if str(card_num) not in user["inventory"]:
                                user["inventory"][str(card_num)] = 5
                            # Add the specified quantity
                            user["inventory"][str(card_num)] += quantity
                        else:
                            # In limitless mode, add the quantity (or unlimited)
                            if str(card_num) not in user["inventory"]:
                                user["inventory"][str(card_num)] = 0
                            user["inventory"][str(card_num)] += quantity
                        
                        added_cards.append(f"#{card_num} x{quantity}")
                    except ValueError:
                        await message.channel.send(f"Invalid input: '{line}'. Skipping.")
            
            if added_cards:
                save_data()
                await message.channel.send(f"Added: {', '.join(added_cards)}\nUse `$use` to equip them to your active deck.")
            else:
                await message.channel.send("No valid cards added.")
                
        except TimeoutError:
            await message.channel.send("Command timed out. Please try again.")
        return

    # CARDS COMMAND (Inventory)
    if content.startswith('$cards'):
        inventory = user["inventory"]
        if not inventory:
            await message.channel.send("Your inventory is empty. Use `$add` to add cards.")
            return
        
        result = "**Your Cards (Inventory):**\n"
        for card_num, quantity in inventory.items():
            card_num = int(card_num)
            if card_num in card_library:
                card = card_library[card_num]
                if user["deck_mode"] == "limitless":
                    result += f"{card_num}. {card['name']} - ∞ (Limitless)\n"
                else:
                    result += f"{card_num}. {card['name']} - {quantity}x\n"
        
        await message.channel.send(result[:2000])
        return

    # USE COMMAND - Add cards to active deck
    if content.startswith('$use'):
        parts = content.split()
        if len(parts) < 2:
            await message.channel.send("Please specify which cards to use. Example: `$use 1 2 3`")
            return
        
        added_cards = []
        for part in parts[1:]:
            try:
                card_num = int(part)
                if card_num not in card_library:
                    await message.channel.send(f"Card #{card_num} not found in library.")
                    continue
                
                # Check if user has the card in inventory
                if str(card_num) not in user["inventory"] or user["inventory"][str(card_num)] <= 0:
                    await message.channel.send(f"You don't have card #{card_num} in your inventory.")
                    continue
                
                # Add to active deck
                user["active_deck"].append(card_num)
                
                # Remove from inventory if limited mode
                if user["deck_mode"] == "limited":
                    user["inventory"][str(card_num)] -= 1
                    if user["inventory"][str(card_num)] <= 0:
                        del user["inventory"][str(card_num)]
                # In limitless mode, keep in inventory
                
                added_cards.append(f"#{card_num}")
            except ValueError:
                await message.channel.send(f"Invalid card number: '{part}'")
        
        if added_cards:
            save_data()
            # Show the updated active deck
            deck_display = format_active_deck(user["active_deck"])
            await message.channel.send(f"Added: {', '.join(added_cards)}\n```\n{deck_display}```")
        else:
            await message.channel.send("No valid cards added.")
        return

    # DECK COMMAND - Show active deck
    if content.startswith('$deck'):
        deck = user["active_deck"]
        if not deck:
            await message.channel.send("Your active deck is empty. Use `$use` or `$plus` to add cards.")
            return
        
        deck_display = format_active_deck(deck)
        await message.channel.send(f"**Your Active Deck:**\n```\n{deck_display}```")
        return

    # PLUS COMMAND - Add card to active deck (even after draw)
    if content.startswith('$plus'):
        parts = content.split()
        if len(parts) < 2:
            await message.channel.send("Please specify which card to add. Example: `$plus 1`")
            return
        
        added_cards = []
        for part in parts[1:]:
            try:
                card_num = int(part)
                if card_num not in card_library:
                    await message.channel.send(f"Card #{card_num} not found in library.")
                    continue
                
                # Check if user has the card in inventory
                if str(card_num) not in user["inventory"] or user["inventory"][str(card_num)] <= 0:
                    await message.channel.send(f"You don't have card #{card_num} in your inventory.")
                    continue
                
                # Add to active deck
                user["active_deck"].append(card_num)
                
                # Remove from inventory if limited mode
                if user["deck_mode"] == "limited":
                    user["inventory"][str(card_num)] -= 1
                    if user["inventory"][str(card_num)] <= 0:
                        del user["inventory"][str(card_num)]
                
                added_cards.append(f"#{card_num}")
            except ValueError:
                await message.channel.send(f"Invalid card number: '{part}'")
        
        if added_cards:
            save_data()
            deck_display = format_active_deck(user["active_deck"])
            await message.channel.send(f"Added to active deck: {', '.join(added_cards)}\n```\n{deck_display}```")
        else:
            await message.channel.send("No valid cards added.")
        return

    # DRAW COMMAND
    if content.startswith('$draw'):
        if not user["active_deck"]:
            await message.channel.send("You have no cards in your active deck! Use `$use # # #` to add cards first.")
            return
        
        # Draw 6 cards from active deck
        drawn_cards = random.sample(user["active_deck"], min(6, len(user["active_deck"])))
        
        # If not enough cards, add more from inventory if available
        while len(drawn_cards) < 6:
            # Try to add more cards from inventory
            available_cards = [int(k) for k, v in user["inventory"].items() if v > 0]
            if available_cards:
                new_card = random.choice(available_cards)
                drawn_cards.append(new_card)
                # Remove from active deck if limited mode
                if user["deck_mode"] == "limited":
                    user["inventory"][str(new_card)] -= 1
                    if user["inventory"][str(new_card)] <= 0:
                        del user["inventory"][str(new_card)]
            else:
                break
        
        # Ensure category balance
        drawn_cards = ensure_category_balance(drawn_cards)
        
        # Store in hand
        user["hand"] = drawn_cards
        
        # Clear active deck after draw
        user["active_deck"] = []
        
        save_data()
        
        # Display the hand
        hand_display = format_hand(drawn_cards)
        await message.channel.send(f"**Your Drawn Cards:**\n```\n{hand_display}```")
        return

    # HAND COMMAND
    if content.startswith('$hand'):
        if not user["hand"]:
            await message.channel.send("You have no cards in hand. Use `$draw` to draw cards.")
            return
        
        hand_display = format_hand(user["hand"])
        await message.channel.send(f"**Your Current Hand:**\n```\n{hand_display}```")
        return

    # X COMMAND - Reroll cards
    if content.startswith('$x'):
        parts = content.split()
        if len(parts) < 2:
            await message.channel.send("Please specify which cards to reroll. Example: `$x 1 3`")
            return
        
        if not user["hand"]:
            await message.channel.send("You have no cards in hand. Use `$draw` first.")
            return
        
        # Get indices to reroll
        indices = []
        for part in parts[1:]:
            try:
                idx = int(part) - 1
                if 0 <= idx < len(user["hand"]):
                    indices.append(idx)
                else:
                    await message.channel.send(f"Card {idx+1} is not in your hand.")
            except ValueError:
                await message.channel.send(f"Invalid input: '{part}'. Please use numbers.")
                return
        
        if not indices:
            await message.channel.send("No valid cards to reroll.")
            return
        
        # Calculate total MP cost for rerolling
        total_mp_cost = 0
        for idx in indices:
            card_num = user["hand"][idx]
            if card_num in card_library:
                card = card_library[card_num]
                if card["mp"] != "Variable":
                    total_mp_cost += card["mp"]
                else:
                    # For variable cost cards, use a default of 2
                    total_mp_cost += 2
        
        # Check if user has enough MP (can go negative but not above cap)
        if user["mp"] < total_mp_cost and user["mp_cap"] > 0:
            await message.channel.send(f"You don't have enough MP! You have {user['mp']} Mp, need {total_mp_cost} Mp.")
            return
        
        # Deduct MP
        user["mp"] -= total_mp_cost
        
        # Reroll selected cards
        for idx in indices:
            # Get card type of the one being replaced
            old_card = user["hand"][idx]
            old_type = card_library[old_card]["type"] if old_card in card_library else None
            
            # Find a new card of the same type
            possible_cards = [num for num, card in card_library.items() 
                            if card["type"] == old_type and num not in user["hand"]]
            if possible_cards:
                new_card = random.choice(possible_cards)
                user["hand"][idx] = new_card
        
        # Ensure category balance
        user["hand"] = ensure_category_balance(user["hand"])
        
        save_data()
        
        hand_display = format_hand(user["hand"])
        await message.channel.send(f"**Rerolled Cards!** (Cost: {total_mp_cost} Mp)\n```\n{hand_display}```")
        return

    # R COMMAND - Smart d20 roll
    if content.startswith('$r'):
        roll = smart_d20_roll(user_id)
        streak_info = f"Bad streak: {int(user['bad_luck_streak'])} | Good streak: {int(user['good_luck_streak'])}"
        
        if roll <= 5:
            await message.channel.send(f"🎲 You rolled a **{roll}**! (Critical fail!)\n{streak_info}")
        elif roll <= 10:
            await message.channel.send(f"🎲 You rolled a **{roll}**. (Not great)\n{streak_info}")
        elif roll <= 15:
            await message.channel.send(f"🎲 You rolled a **{roll}**. (Solid roll!)\n{streak_info}")
        elif roll <= 19:
            await message.channel.send(f"🎲 You rolled a **{roll}**! (Great roll!)\n{streak_info}")
        else:
            await message.channel.send(f"🎲 You rolled a **{roll}**! (Critical success!)\n{streak_info}")
        
        save_data()
        return

    # MP TURN COMMAND
    if content.startswith('$mp turn'):
        recovery = user["mp_recovery"]
        user["mp"] += recovery
        
        # Check MP cap
        if user["mp_cap"] > 0 and user["mp"] > user["mp_cap"]:
            user["mp"] = user["mp_cap"]
        
        save_data()
        await message.channel.send(f"Added {recovery} Mp! Current MP: {user['mp']} Mp")
        return

    # SETTINGS COMMAND
    if content.startswith('$settings'):
        parts = content.split()
        if len(parts) < 2:
            await message.channel.send("Available settings:\n`$settings turn #` - Set MP recovery\n`$settings deck limited/limitless` - Set deck mode")
            return
        
        if parts[1] == "turn":
            if len(parts) < 3:
                await message.channel.send("Please specify a number. Example: `$settings turn 5`")
                return
            try:
                new_recovery = int(parts[2])
                user["mp_recovery"] = new_recovery
                save_data()
                await message.channel.send(f"MP recovery set to {new_recovery} Mp per turn.")
            except ValueError:
                await message.channel.send("Please provide a valid number.")
        
        elif parts[1] == "deck":
            if len(parts) < 3:
                await message.channel.send("Please specify 'limited' or 'limitless'. Example: `$settings deck limited`")
                return
            mode = parts[2].lower()
            if mode in ["limited", "limitless"]:
                user["deck_mode"] = mode
                save_data()
                await message.channel.send(f"Deck mode set to: {mode}")
            else:
                await message.channel.send("Invalid mode. Choose 'limited' or 'limitless'.")
        return

    # RESET ALL COMMAND
    if content.startswith('$reset all'):
        # Ask for confirmation
        await message.channel.send("⚠️ **WARNING**: This will reset ALL data for EVERYONE! Type `$confirm reset` to confirm.")
        
        def check(m):
            return m.author == message.author and m.channel == message.channel
        
        try:
            msg = await client.wait_for('message', timeout=30.0, check=check)
            if msg.content.lower() == '$confirm reset':
                user_data.clear()
                save_data()
                await message.channel.send("✅ All data has been reset!")
            else:
                await message.channel.send("Reset cancelled.")
        except TimeoutError:
            await message.channel.send("Reset cancelled (timeout).")
        return

    # NUM COMMAND - Modify card quantities
    if content.startswith('$num'):
        parts = content.split()
        if len(parts) < 2:
            await message.channel.send("Usage: `$num # +/-#` or `$num random #/all`")
            return
        
        if parts[1] == "random":
            if len(parts) < 3:
                await message.channel.send("Usage: `$num random #` or `$num random all`")
                return
            
            if parts[2] == "all":
                # Randomize all cards in inventory
                for card_num in user["inventory"]:
                    user["inventory"][card_num] = random.randint(1, 10)
                save_data()
                await message.channel.send("All card quantities randomized!")
                return
            else:
                try:
                    card_num = int(parts[2])
                    if str(card_num) not in user["inventory"]:
                        await message.channel.send(f"You don't have card #{card_num} in your inventory.")
                        return
                    user["inventory"][str(card_num)] = random.randint(1, 10)
                    save_data()
                    await message.channel.send(f"Card #{card_num} quantity randomized!")
                except ValueError:
                    await message.channel.send("Please provide a valid card number.")
                return
        
        elif len(parts) == 3:
            try:
                card_num = int(parts[1])
                change = int(parts[2])
                
                if str(card_num) not in user["inventory"]:
                    await message.channel.send(f"You don't have card #{card_num} in your inventory.")
                    return
                
                user["inventory"][str(card_num)] += change
                
                if user["inventory"][str(card_num)] <= 0:
                    del user["inventory"][str(card_num)]
                    await message.channel.send(f"Card #{card_num} removed from inventory.")
                else:
                    await message.channel.send(f"Card #{card_num} quantity is now {user['inventory'][str(card_num)]}")
                
                save_data()
            except ValueError:
                await message.channel.send("Please provide valid numbers.")
        else:
            await message.channel.send("Usage: `$num # +/-#` or `$num random #/all`")
        return

    # Keep existing functionality
    if content.startswith('roll d20'):
        roll_result = random.randint(1, 20)
        if roll_result < 2:
            await message.channel.send(f'You rolled a d20 and got {roll_result} dm, kill this mf.')
        elif roll_result < 10:
            await message.channel.send(f'You rolled a d20 and got {roll_result} get fucked lmao!')
        elif roll_result < 20:
            await message.channel.send(f'You rolled a d20 and got {roll_result} not bad!')
        else:
            await message.channel.send(f'You rolled a d20 and got {roll_result} sheeeesh')

    if ":sob:" in message.content:
        await message.channel.send("L")

# Run the bot
if __name__ == "__main__":
    try:
        token = os.getenv("DISCORD_BOT_TOKEN")
        
        if not token:
            token = "YOUR_BOT_TOKEN_HERE"
        
        if token == "YOUR_BOT_TOKEN_HERE" or not token:
            print("="*50)
            print("ERROR: Please set your Discord bot token!")
            print("="*50)
            print("1. Go to Discord Developer Portal")
            print("2. Get your bot token")
            print("3. Set it as environment variable DISCORD_BOT_TOKEN")
            print("4. NEVER commit real tokens to GitHub!")
        else:
            print("Starting bot...")
            client.run(token)
            
    except discord.LoginFailure as e:
        print(f"Login failed: {e}")
        print("Please check your token is correct and not expired.")
    except discord.HTTPException as e:
        if e.status == 429:
            print("Rate limited - too many requests")
        else:
            raise e
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
