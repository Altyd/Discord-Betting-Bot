import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import random
import json
import os

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
current_bet = None
DATA_FILE = "user_data.json"

# Load and save user data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)

def get_user_data(user_id):
    data = load_data()
    user_id_str = str(user_id)
    
    # Ensure user data exists with default values
    if user_id_str not in data:
        data[user_id_str] = {"balance": 1000, "loan": 0}
    
    # Ensure all keys are present in the user's data
    if "items" not in data[user_id_str]:
        data[user_id_str]["items"] = []
    
    # Save any changes back to ensure defaults are persisted
    save_data(data)
    
    return data[user_id_str]


def update_user_data(user_id, balance=None, loan=None, items=None):
    data = load_data()
    user_id_str = str(user_id)
    
    # Ensure user data exists
    if user_id_str not in data:
        data[user_id_str] = {"balance": 1000, "loan": 0}
    
    # Update balance and loan if provided
    if balance is not None:
        data[user_id_str]["balance"] = balance
    if loan is not None:
        data[user_id_str]["loan"] = loan
    
    # Update items if provided
    if items is not None:
        # Ensure "items" is initialized as a list if it doesn't exist
        if "items" not in data[user_id_str]:
            data[user_id_str]["items"] = []
        data[user_id_str]["items"] = items
    
    # Save the updated data
    save_data(data)


# Bot commands
@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")

@bot.command(name="balance", help="Check your balance.")
async def balance(ctx):
    user_data = get_user_data(ctx.author.id)
    await ctx.send(
        f"{ctx.author.mention}, your balance is {user_data['balance']} coins. "
        f"Debt: {user_data['loan']} coins."
    )
@bot.command(name="loan", help="Apply for a loan.")
async def loan(ctx, amount: int):
    user_data = get_user_data(ctx.author.id)
    item_prices = {
        "Rolex": 5000,
        "Lambo": 130000,
        "Porsche": 100000,
        "Apartment": 200000,
        "Penthouse": 1000000,
        "JetSki": 15000,
        "PrivateIsland": 5000000,
        "Helicopter": 800000,
        "Superyacht": 7500000,
        "Diamond Ring": 10000,
        "SpaceShuttle": 20000000,
        "Hooker": 50000,
        "SecurityTeam": 9000000,
        "PrivateJet": 3000000,
        "Castle": 15000000
    }

    # Check if the user already has a loan
    if user_data["loan"] > 0:
        await ctx.send(f"{ctx.author.mention}, you must repay your current loan first!")
        return

    # Get user balance and assets
    balance = user_data.get("balance", 0)
    assets_value = sum(item_prices.get(item, 0) for item in user_data.get("items", []))  # Calculate total asset value

    # Determine maximum loan amount
    max_loan = max(5000, assets_value) if balance < 5000 else assets_value
    if amount > max_loan:
        await ctx.send(f"{ctx.author.mention}, you can only take a loan up to {max_loan} coins.")
        return

    # Update balance and loan with 100% interest
    user_data["balance"] += amount
    user_data["loan"] = amount * 2  # 100% interest
    update_user_data(ctx.author.id, user_data["balance"], user_data["loan"])

    await ctx.send(f"{ctx.author.mention}, loan approved! Balance: {user_data['balance']}, Debt: {user_data['loan']}.")


@bot.command(name="repay", help="Repay your loan.")
async def repay(ctx, amount: int):
    user_data = get_user_data(ctx.author.id)
    if user_data["loan"] == 0:
        await ctx.send(f"{ctx.author.mention}, you have no loans to repay.")
        return
    if amount > user_data["balance"]:
        await ctx.send(f"{ctx.author.mention}, you don't have enough coins!")
        return
    repayment = min(amount, user_data["loan"])
    user_data["balance"] -= repayment
    user_data["loan"] -= repayment
    update_user_data(ctx.author.id, user_data["balance"], user_data["loan"])
    await ctx.send(f"{ctx.author.mention}, you repaid {repayment} coins. Debt remaining: {user_data['loan']}.")

@bot.command(name="leaderboard", help="Show the leaderboard.")
async def leaderboard(ctx):
    data = load_data()
    
    if not data:
        await ctx.send("No data available to display on the leaderboard.")
        return
    
    # Sort users by balance in descending order
    leaderboard = sorted(data.items(), key=lambda x: x[1]["balance"], reverse=True)
    
    if not leaderboard:
        await ctx.send("No users with balances found.")
        return
    
    leaderboard_msg = "**Leaderboard**\n"
    for user_id, info in leaderboard:
        debt = info.get("loan", 0)  # Default to 0 if 'loan' is not found
        balance = info.get("balance", 0)  # Default to 0 if 'balance' is not found
        leaderboard_msg += f"<@{user_id}>: {balance} coins (Debt: {debt})\n"
    
    await ctx.send(leaderboard_msg)


@bot.command(name="rps", help="Play Rock, Paper, Scissors.")
async def rps(ctx, bet: int, choice: str):
    user_data = get_user_data(ctx.author.id)
    if bet > user_data["balance"]:
        await ctx.send(f"{ctx.author.mention}, you don't have enough coins to bet.")
        return
    choices = ["rock", "paper", "scissors"]
    if choice not in choices:
        await ctx.send(f"{ctx.author.mention}, choose rock, paper, or scissors.")
        return
    bot_choice = random.choice(choices)
    user_data["balance"] -= bet
    result = "lose"
    if (choice == "rock" and bot_choice == "scissors") or \
       (choice == "paper" and bot_choice == "rock") or \
       (choice == "scissors" and bot_choice == "paper"):
        user_data["balance"] += bet * 2
        result = "win"
    elif choice == bot_choice:
        user_data["balance"] += bet  # Tie, refund the bet
        result = "tie"
    update_user_data(ctx.author.id, user_data["balance"])
    await ctx.send(
        f"{ctx.author.mention}, you chose {choice}, I chose {bot_choice}. You {result}! "
        f"New balance: {user_data['balance']} coins."
    )

@bot.command(name="slots", help="Play the slot machine.")
async def slots(ctx, bet: int):
    user_data = get_user_data(ctx.author.id)
    if bet > user_data["balance"]:
        await ctx.send(f"{ctx.author.mention}, you don't have enough coins.")
        return
    user_data["balance"] -= bet
    spin = [random.choice(["🍒", "🍋", "🔔", "🍀", "🍉"]) for _ in range(3)]
    if len(set(spin)) == 1:
        winnings = bet * 3
        user_data["balance"] += winnings
        result = f"You won {winnings} coins!"
    else:
        result = "You lost!"
    update_user_data(ctx.author.id, user_data["balance"])
    await ctx.send(f"{ctx.author.mention}, {' | '.join(spin)} - {result} Balance: {user_data['balance']} coins.")

@bot.command(name="reset_balances", help="Reset all balances. (Admins only)")
@has_permissions(administrator=True)
async def reset_balances(ctx):
    data = load_data()
    for user_id in data:
        data[user_id]["balance"] = 1000
        data[user_id]["loan"] = 0
    save_data(data)
    await ctx.send("All balances have been reset.")
    
# Command to start a new bet with separate payouts for win/lose
@bot.command(name='start_bet', help='Start a new bet. (Admins only)')
@has_permissions(administrator=True)
async def start_bet(ctx, reason: str, win_payout: float, lose_payout: float):
    global current_bet, bet_placements

    if current_bet:
        await ctx.send("A bet is already active. Resolve it before starting a new one.")
        return

    # Create the new bet with specific payouts for win/lose
    current_bet = {"reason": reason, "win_payout": win_payout, "lose_payout": lose_payout}
    bet_placements = {}
    await ctx.send(f"A new bet has started: **{reason}**\nWin Payout: **{win_payout}x**\nLose Payout: **{lose_payout}x**\nPlace your bets with `!bet <amount> <win/lose>`.")

# Command to place a bet
@bot.command(name='bet', help='Place a bet on the current game.')
async def bet(ctx, amount: int, prediction: str):
    global current_bet, bet_placements

    user_id = ctx.author.id
    user_data = get_user_data(user_id)

    if not current_bet:
        await ctx.send("No active bet to place your wager on.")
        return

    if prediction.lower() not in ['win', 'lose']:
        await ctx.send("Invalid prediction. Use 'win' or 'lose'.")
        return

    if amount > user_data["balance"]:
        await ctx.send(f"{ctx.author.mention}, you don't have enough coins to place this bet.")
        return

    if user_id in bet_placements:
        await ctx.send(f"{ctx.author.mention}, you've already placed a bet on this round.")
        return

    # Deduct bet amount and record the placement
    user_data["balance"] -= amount
    bet_placements[user_id] = {"amount": amount, "prediction": prediction.lower()}
    update_user_data(user_id, user_data["balance"])

    await ctx.send(f"{ctx.author.mention}, you placed a bet of {amount} coins predicting '{prediction}'.")

# Command to resolve the bet and payout separately for win/lose predictions
# Command to resolve the bet and payout separately for win/lose predictions
@bot.command(name='resolve_bet', help='Resolve the current bet. (Admins only)')
@has_permissions(administrator=True)
async def resolve_bet(ctx, outcome: str):
    global current_bet, bet_placements

    if not current_bet:
        await ctx.send("No active bet to resolve.")
        return

    if outcome.lower() not in ['win', 'lose']:
        await ctx.send("Invalid outcome. Use 'win' or 'lose'.")
        return

    # Save current bet's reason and outcome before clearing the bet
    reason = current_bet['reason']
    win_payout = current_bet['win_payout']
    lose_payout = current_bet['lose_payout']

    # Get the specific payout multiplier based on the outcome
    payout = win_payout if outcome.lower() == 'win' else lose_payout
    results = []

    # Process payouts for each bet placement
    for user_id, bet in bet_placements.items():
        user_data = get_user_data(user_id)
        
        if bet["prediction"] == outcome.lower():
            winnings = bet["amount"] * payout
            user_data["balance"] += winnings
            results.append(f"<@{user_id}> won {winnings} coins!")
        else:
            results.append(f"<@{user_id}> lost their bet of {bet['amount']} coins.")
        
        update_user_data(user_id, user_data["balance"])

    # Reset the bet placements and current bet
    bet_placements = {}
    current_bet = None

    winners_message = "\n".join(results) if results else "No winners this time."
    await ctx.send(f"**Bet Resolved: {reason}**\nResult: **{outcome.capitalize()}**\n\n{winners_message}")

# Command to send money to another user
@bot.command(name='send', help='Send coins to another user.')
async def send(ctx, recipient: discord.User, amount: int):
    sender_id = ctx.author.id
    recipient_id = recipient.id

    # Fetch sender data
    sender_data = get_user_data(sender_id)
    if sender_data["loan"] > 0:
        await ctx.send(f"{ctx.author.mention}, you must repay your current loan first!")
        return
    if amount <= 0:
        await ctx.send(f"{ctx.author.mention}, you can't send a negative or zero amount.")
        return

    if sender_data["balance"] < amount:
        await ctx.send(f"{ctx.author.mention}, you don't have enough coins to send that amount.")
        return

    # Fetch recipient data (make sure the recipient has a record)
    recipient_data = get_user_data(recipient_id)
    
    if not recipient_data:
        await ctx.send(f"{ctx.author.mention}, the recipient doesn't have a valid account.")
        return

    # Deduct from sender and add to recipient
    sender_data["balance"] -= amount
    recipient_data["balance"] += amount

    # Update both users' balances in the data storage
    update_user_data(sender_id, sender_data["balance"])
    update_user_data(recipient_id, recipient_data["balance"])

    await ctx.send(f"{ctx.author.mention} successfully sent {amount} coins to {recipient.mention}.")

@bot.command(name='strip', help='Become a stripper and make money from -200 to 500 coins.')
async def strip(ctx):
    user_id = ctx.author.id

    # Fetch user data
    user_data = get_user_data(user_id)

    # Generate a random amount between -200 and 500
    amount = random.randint(-200, 500)

    # Update balance
    user_data["balance"] += amount

    # Save updated data
    update_user_data(user_id, user_data["balance"])

    # Prepare response message
    if amount >= 0:
        await ctx.send(f"{ctx.author.mention} stripped and earned **{amount}** coins!")
    else:
        await ctx.send(f"{ctx.author.mention} stripped and lost **{-amount}** coins... Better luck next time!")
        
        
SHOP_ITEMS = {
    "⌚ Rolex": 5000,
    "🏎️ Lambo": 130000,
    "🚘 Porsche": 100000,
    "🏢 Apartment": 200000,
    "🌆 Penthouse": 1000000,
    "🛥️ JetSki": 15000,
    "🏝️ PrivateIsland": 5000000,
    "🚁 Helicopter": 800000,
    "🛳️ Superyacht": 7500000,
    "💍 DiamondRing": 10000,
    "🚀 SpaceShuttle": 20000000,
    "💃 Hooker": 50000,
    "🛡️ SecurityTeam": 9000000,
    "✈️ PrivateJet": 3000000,
    "🏰 Castle": 15000000
}
@bot.command(name='buy', help='Purchase an item from the shop.')
async def buy(ctx, item: str):
    user_id = ctx.author.id
    user_data = get_user_data(user_id)

    # Define the item prices
    item_prices = {
        "Rolex": 5000,
        "Lambo": 130000,
        "Porsche": 100000,
        "Apartment": 200000,
        "Penthouse": 1000000,
        "JetSki": 15000,
        "PrivateIsland": 5000000,
        "Helicopter": 800000,
        "Superyacht": 7500000,
        "Diamond Ring": 10000,
        "SpaceShuttle": 20000000,
        "Hooker": 50000,
        "SecurityTeam": 9000000,
        "PrivateJet": 3000000,
        "Castle": 15000000
    }

    # Check if the item exists in the shop
    if item not in item_prices:
        await ctx.send(f"{ctx.author.mention}, this item is not available in the shop.")
        return

    # Check if the user can afford the item
    if user_data["balance"] < item_prices[item]:
        await ctx.send(f"{ctx.author.mention}, you don't have enough balance to buy the {item}.")
        return

    # Deduct the price of the item from the user's balance
    user_data["balance"] -= item_prices[item]

    # Add the item to the user's inventory
    items = user_data.get("items", [])
    items.append(item)

    # Save the updated data
    update_user_data(user_id, balance=user_data["balance"], items=items)

    await ctx.send(f"{ctx.author.mention} successfully purchased a {item}!")



@bot.command(name='sell', help='Sell an item from your inventory.')
async def sell(ctx, item: str):
    user_id = ctx.author.id
    user_data = get_user_data(user_id)

    item_prices = {
        "Rolex": 5000,
        "Lambo": 130000,
        "Porsche": 100000,
        "Apartment": 200000,
        "Penthouse": 1000000,
        "JetSki": 15000,
        "PrivateIsland": 5000000,
        "Helicopter": 800000,
        "Superyacht": 7500000,
        "Diamond Ring": 10000,
        "SpaceShuttle": 20000000,
        "Hooker": 50000,
        "SecurityTeam": 9000000,
        "PrivateJet": 3000000,
        "Castle": 15000000
    }

    # Validate user data structure
    if not isinstance(user_data.get("balance"), (int, float)):
        user_data["balance"] = 1000  # Reset to default value if corrupted

    if "items" not in user_data or item not in user_data["items"]:
        await ctx.send(f"{ctx.author.mention}, you don't own a {item}.")
        return

    # Calculate the sell price (70% of the original value)
    sell_price = item_prices[item] * 0.7

    # Remove the item from inventory
    user_data["items"].remove(item)

    # Add the sell price to the user's balance
    user_data["balance"] += sell_price

    # Save the updated data
    update_user_data(user_id, balance=user_data["balance"], items=user_data["items"])

    await ctx.send(f"{ctx.author.mention} successfully sold the {item} for {sell_price:.2f} coins!")


@bot.command(name='shop', help='View the shop and available items.')
async def shop(ctx):
    shop_items = "\n".join([f"{item}: {price} coins" for item, price in SHOP_ITEMS.items()])
    await ctx.send(f"**Welcome to the Shop!**\nHere are the available items:\n{shop_items}\nUse `!buy <item>` to purchase an item.")
@bot.command(name='inventory', help='Check your inventory of items.')
async def inventory(ctx):
    user_id = ctx.author.id
    user_data = get_user_data(user_id)

    # Check if the user has any items
    if "items" not in user_data or not user_data["items"]:
        await ctx.send(f"{ctx.author.mention}, your inventory is empty.")
        return

    # Format and display the items in the user's inventory
    inventory_items = "\n".join(user_data["items"])
    await ctx.send(f"{ctx.author.mention}, your inventory contains:\n{inventory_items}")

@bot.command(name='commands', help='List all commands.')
async def commands_list(ctx):
    """List all commands."""
    commands = """
    **Commands List:**
    - !balance: Check your balance and loans.
    - !loan <amount>: Apply for a loan.
    - !repay <amount>: Repay your loan.
    - !leaderboard: Show the leaderboard.
    - !rps <bet> <choice>: Play Rock, Paper, Scissors with a bet.
    - !slots <bet>: Play the slot machine with a bet.
    - !reset_balances: Reset all balances. (Admins only)
    - !start_bet <reason> <odds win> <odds lose>: Start a new bet. (Admins only)
    - !bet <amount> <win/lose>: Place a bet on the current game.
    - !resolve_bet <win/lose>: Resolve the current bet and payout winnings. (Admins only)
    - !send: <person> <amount>
    - !strip: Become a stripper and make money
    - !shop: Check things to buy
    - !inventory: Check inventory
    - !buy: Buy things
    - !sell: Sell things to afford your addiction
    - !doors <amount>: Choose a door and gamble
    - !current_bet: Check the status of the current bet.
    """
    await ctx.send(commands)
# Helper function for Mines game
def generate_grid(size, mines):
    grid = ['0'] * (size * size)  # 5x5 grid flattened
    mine_positions = random.sample(range(size * size), mines)
    for mine in mine_positions:
        grid[mine] = '💣'  # Marking mines
    return grid

def display_grid(grid, revealed_tiles):
    display = ""
    for i in range(5):  # 5x5 grid
        display += " ".join(
            [grid[i*5 + j] if (i*5 + j) in revealed_tiles else '⬛' for j in range(5)]
        ) + "\n"
    return display

@bot.command(name="mines", help="Play a game of Mines.")
async def mines(ctx, bet: int, num_mines: int):
    user_id = ctx.author.id

    # Get the user data and check balance
    user_data = get_user_data(user_id)
    if user_data["balance"] < bet:
        await ctx.send(f"{ctx.author.mention}, you don't have enough balance to play this game!")
        return

    # Deduct the bet from the user's balance
    user_data["balance"] -= bet
    update_user_data(user_id, balance=user_data["balance"])

    # Generate the grid with mines
    grid = generate_grid(5, num_mines)
    revealed_tiles = set()  # Keep track of revealed tiles

    # Send the grid to the user and add reactions
    grid_message = await ctx.send(f"**Mines Game!**\nYour bet: {bet} 💸\n{display_grid(grid, revealed_tiles)}\nReact with the numbers (1-25) to reveal tiles!")

    # Add reactions for clicking the grid (1-25)
    for i in range(1, 26):
        await grid_message.add_reaction(str(i))

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in [str(i) for i in range(1, 26)]

    # Game loop
    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)

            # Get the tile number from the emoji
            tile_num = int(reaction.emoji) - 1
            if tile_num in revealed_tiles:
                await ctx.send(f"{ctx.author.mention}, this tile has already been revealed.")
                continue

            # Reveal the tile
            revealed_tiles.add(tile_num)
            if grid[tile_num] == '💣':
                # User clicked on a mine, game over
                await ctx.send(f"{ctx.author.mention}, you hit a mine! You lost your bet of {bet} 💸.")
                update_user_data(user_id, balance=user_data["balance"] - bet)  # Subtract the bet from the user's balance
                break
            else:
                # Display the updated grid
                updated_grid = grid[:]
                for idx in revealed_tiles:
                    updated_grid[idx] = '✅'  # Mark revealed tiles with a check mark

                updated_grid_display = display_grid(updated_grid, revealed_tiles)
                await grid_message.edit(content=f"**Mines Game!**\nYour bet: {bet} 💸\n{updated_grid_display}\nReact with the numbers (1-25) to reveal more tiles!")

        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention}, the game timed out!")
            break

        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
            break
import random
import asyncio

@bot.command(name="doors", help="Choose a door to find the money! Usage: !doors <amount>")
async def doors(ctx, amount: int):
    user_id = ctx.author.id
    user_data = get_user_data(user_id)
    
    # Validate the bet amount
    if amount <= 0:
        await ctx.send(f"{ctx.author.mention}, please enter a valid bet amount!")
        return

    if amount > user_data["balance"]:
        await ctx.send(f"{ctx.author.mention}, you don't have enough balance to place this bet.")
        return

    # Deduct the bet amount
    user_data["balance"] -= amount
    update_user_data(user_id, user_data["balance"])

    # Randomly choose the winning door
    winning_door = random.choice(["🟦", "🟨", "🟥"])
    doors = ["🟦", "🟨", "🟥"]

    # Send the game message
    message = await ctx.send(
        f"{ctx.author.mention}, \n Pick a door! \n React with one of the emojis: 🟦 🟨 🟥\n\n"
        f"Bet amount: {amount}"
    )

    # Add reactions for the doors
    for door in doors:
        await message.add_reaction(door)

    # Wait for the user's reaction
    def check(reaction, user):
        return (
            user == ctx.author
            and str(reaction.emoji) in doors
            and reaction.message.id == message.id
        )

    try:
        reaction, _ = await bot.wait_for("reaction_add", timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention}, you took too long to choose a door!")
        return

    # Evaluate the result
    chosen_door = str(reaction.emoji)
    if chosen_door == winning_door:
        multiplier = random.randint(2, 4)  # Payout multiplier
        winnings = amount * multiplier
        user_data["balance"] += winnings  # Add winnings to balance
        result = f"You won {winnings} coins! (Multiplier: x{multiplier})"
    else:
        result = "You lost! The money was behind another door."

    # Save the updated user data
    update_user_data(user_id, user_data["balance"]) 

    # Send the result
    await ctx.send(f"{ctx.author.mention}, {' | '.join([str(reaction.emoji)])} - {result} Balance: {user_data['balance']} coins.")


# Run the bot
bot.run('MTMwNzM5MDgyMzAwODMwOTI5OA.GtAd71.db8fn3jPDY06OTlf47yFVuDzyMJnaJNqB2BJvE')
