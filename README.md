# Discord Economy Bot

This Discord bot allows users to interact with a virtual economy through commands to manage their balance, loans, betting, and shop items. It also includes a game of Rock, Paper, Scissors (RPS), a slot machine, and more. The bot uses various commands for playing, interacting with the economy, and tracking user progress.

## Features

- **Balance Management**: Check balance, take loans, repay loans.
- **Betting System**: Play games like Rock, Paper, Scissors, and place bets on various outcomes.
- **Slot Machine**: Play the slot machine and try your luck!
- **Shop System**: Buy in-game items with your coins.
- **Leaderboard**: View the leaderboard of users with the highest balance.
- **Admin Commands**: Admin-only commands to reset balances and manage betting.
- **Send Coins**: Send coins to other users in the server.
- **Stripper Command**: A random money-generating command to earn or lose coins.

## Setup

### Requirements

- Python 3.x
- [discord.py](https://discordpy.readthedocs.io/en/stable/)
- Random (for randomizing outcomes like betting or the stripper command)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Altyd/Discord-Betting-Bot.git
   cd discord-economy-bot
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the bot token:
    - Create a .env file in the root directory.
    - Add your Discord bot token in the .env file:
    ```bash
    DISCORD_TOKEN=your-bot-token-here
   ```
4. Run the bot:
    ```bash
    python bot.py
   ```
## Commands
### Economy Commands
- !balance: Check your balance and current debt.
- !loan <amount>: Apply for a loan (max loan is based on balance and assets).
- !repay <amount>: Repay your loan.
- !leaderboard: Show the leaderboard with the highest balance.
- !send <@user> <amount>: Send coins to another user.
### Game Commands
- !doors <amount>
- !bet <amount> <win/lose>: Place a bet on a current active bet.
- !rps <bet> <rock/paper/scissors>: Play Rock, Paper, Scissors with a bet.
- !slots <bet>: Play the slot machine with a bet.
### Admin Commands
- !reset_balances: Reset all balances to 1000 coins (Admins only).
- !start_bet <reason> <win_payout> <lose_payout>: Start a new bet (Admins only).
- !resolve_bet <win/lose>: Resolve the current bet and distribute payouts (Admins only).
### Miscellaneous Commands
- !strip: Randomly earn or lose coins by stripping.
### Data Storage
The bot uses a custom data structure to store user balances, loans, and items. Make sure to implement the functions like get_user_data, update_user_data, and load_data to manage these records.

##Logic
### Loans
Logic Flow
User Takes Loan:
-- !loan 5000 → Bot checks for active debt → Approves loan → Adds 5000 to balance → Sets debt to 10 000 (including 100% interest).
-- Message: "You have taken out a loan of 5000 coins. You now owe 10 000 coins, including interest."

User Repays Loan:
-- !repay 2000 → Bot deducts 2000 from balance → Reduces debt to 3500.
-- Message: "You have repaid 2000 coins. Your remaining debt is 3500 coins."
### Wagers
---
Start bet Command
```bash
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
```
Logic Flow:
-- Check if a bet is already active using current_bet → if no active bet exists, start a new one using the provided reason, win_payout, and lose_payout → Reset any previous bet placements → Notify users that a new bet has started.
---
Bet Command
This command allows users to place a bet based on the current active bet, predicting either "win" or "lose".
```bash
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
```
-- Check if an active bet exists →  Validate the prediction as either "win" or "lose" → Check if the user has enough balance to place the bet →  Ensure the user hasn't already placed a bet → Deduct the bet amount from the user's balance and store the bet details →  Notify the user that their bet has been placed successfully


--- 
## Contributing
Feel free to fork the project and create pull requests for bug fixes or improvements. Make sure to follow the code style and write tests for any new features.

## License
This project is licensed under the MIT License - see the [LICENSE](https://opensource.org/license/mit) file for details.

