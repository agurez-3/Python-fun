#!/usr/bin/env python3
"""Casino Games - Modern GUI"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import compileall
import itertools
import threading
import time
import os
import sys
if sys.platform == "win32":
    import winsound

# --- CONFIGURATION ---
INITIAL_BANKROLL = 100.0
MIN_BET = 1.0
MAX_BET = 1000.0

DIFFICULTIES = {
    'easy': {
        'rows': 9,
        'cols': 9,
        'mines': 10,
        'multiplier': 1.5
    },
    'medium': {
        'rows': 16,
        'cols': 16,
        'mines': 40,
        'multiplier': 2.0
    },
    'hard': {
        'rows': 16,
        'cols': 30,
        'mines': 99,
        'multiplier': 2.5
    }
}

# --- MINESWEEPER GAME LOGIC ---
class MinesweeperGame:
    def __init__(self, difficulty='easy'):
        self.difficulty = difficulty
        self.settings = DIFFICULTIES[difficulty]
        self.rows = self.settings['rows']
        self.cols = self.settings['cols']
        self.mines = self.settings['mines']
        
        # Initialize game state
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.flagged = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.game_over = False
        self.game_won = False
        self.first_click = True
        
        self._place_mines()
        self._calculate_numbers()
    
    def _place_mines(self):
        """Randomly place mines on the board"""
        mine_positions = random.sample(
            [(r, c) for r in range(self.rows) for c in range(self.cols)],
            self.mines
        )
        
        for r, c in mine_positions:
            self.board[r][c] = -1
    
    def _calculate_numbers(self):
        """Calculate numbers for adjacent mines"""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == -1:
                    continue
                
                mine_count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            if self.board[nr][nc] == -1:
                                mine_count += 1
                
                self.board[r][c] = mine_count
    
    def reveal_cell(self, row, col):
        """Reveal a cell"""
        if self.game_over or not self._is_valid_position(row, col):
            return False
        
        if self.revealed[row][col] or self.flagged[row][col]:
            return False
        
        if self.first_click and self.board[row][col] == -1:
            self._ensure_safe_first_click(row, col)
        
        self.first_click = False
        
        if self.board[row][col] == -1:
            self.game_over = True
            self.game_won = False
            return True
        
        self._flood_fill(row, col)
        self._check_win_condition()
        return True
    
    def _ensure_safe_first_click(self, row, col):
        """Ensure first click is safe"""
        if self.board[row][col] == -1:
            safe_spots = [(r, c) for r in range(self.rows) 
                          for c in range(self.cols) 
                          if self.board[r][c] != -1 and (r != row or c != col)]
            
            if safe_spots:
                new_r, new_c = random.choice(safe_spots)
                self.board[row][col] = 0
                self.board[new_r][new_c] = -1
                self._calculate_numbers()
    
    def _flood_fill(self, row, col):
        """Reveal cell and adjacent empty cells"""
        if not self._is_valid_position(row, col) or self.revealed[row][col]:
            return
        
        self.revealed[row][col] = True
        
        if self.board[row][col] == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    self._flood_fill(row + dr, col + dc)
    
    def toggle_flag(self, row, col):
        """Toggle flag on a cell"""
        if self.game_over or not self._is_valid_position(row, col):
            return False
        
        if self.revealed[row][col]:
            return False
        
        self.flagged[row][col] = not self.flagged[row][col]
        return True
    
    def _check_win_condition(self):
        """Check if player has won"""
        revealed_count = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if self.revealed[r][c]:
                    revealed_count += 1
        
        total_cells = self.rows * self.cols
        safe_cells = total_cells - self.mines
        
        if revealed_count == safe_cells:
            self.game_over = True
            self.game_won = True
    
    def _is_valid_position(self, row, col):
        """Check if position is valid"""
        return 0 <= row < self.rows and 0 <= col < self.cols
    
    def is_game_over(self):
        return self.game_over
    
    def is_game_won(self):
        return self.game_won

# --- GAMBLING SYSTEM ---
class GamblingSystem:
    def __init__(self):
        self.bankroll = INITIAL_BANKROLL
        self.current_bet = 0.0
        self.current_difficulty = 'easy'
    
    def place_bet(self, amount, difficulty):
        """Place a bet"""
        if amount < MIN_BET or amount > MAX_BET:
            return False, f"Bet must be between ${MIN_BET} and ${MAX_BET}"
        
        if amount > self.bankroll:
            return False, "Insufficient funds"
            
        self.current_bet = amount
        self.current_difficulty = difficulty
        return True, f"Bet placed: ${amount} on {difficulty} difficulty"
    
    def win_game(self):
        """Handle win"""
        payout = self.current_bet * DIFFICULTIES[self.current_difficulty]['multiplier']
        self.bankroll += payout
        profit = payout - self.current_bet
        
        result = {
            'outcome': 'win',
            'payout': payout,
            'profit': profit,
            'new_bankroll': self.bankroll
        }
        
        self.current_bet = 0.0
        return result
    
    def lose_game(self):
        """Handle loss"""
        loss = self.current_bet
        self.bankroll -= loss
        
        result = {
            'outcome': 'lose',
            'loss': loss,
            'new_bankroll': self.bankroll
        }
        
        self.current_bet = 0.0
        return result

# --- CASINO GAME STUBS ---
class BlackjackGame:
    def __init__(self, gui):
        self.gui = gui
        self.gambling = gui.gambling
        self.window = None
        self.deck = []
        self.player_hand = []
        self.dealer_hand = []
        self.bet = 0
        self.bankroll_label = None
        self.result_label = None
        self.player_label = None
        self.dealer_label = None
        self.hit_btn = None
        self.stand_btn = None

    def start(self):
        self.window = tk.Toplevel(self.gui.root)
        self.window.title("Blackjack")
        self.window.geometry("600x500")
        self.window.configure(bg='#222831')
        self.bankroll_label = tk.Label(self.window, text=f"Bankroll: ${self.gambling.bankroll:.2f}", font=('Arial', 14), fg='#FFD369', bg='#222831')
        self.bankroll_label.pack(pady=10)
        tk.Label(self.window, text="Place your bet:", font=('Arial', 14), fg='#EEEEEE', bg='#222831').pack(pady=5)
        bet_var = tk.DoubleVar()
        bet_entry = tk.Entry(self.window, textvariable=bet_var, font=('Arial', 12))
        bet_entry.pack(pady=5)
        self.result_label = tk.Label(self.window, text="", font=('Arial', 14), fg='#FFD369', bg='#222831')
        self.result_label.pack(pady=10)

        def start_hand():
            bet = bet_var.get()
            max_bet = min(self.gambling.bankroll, MAX_BET)
            if bet < MIN_BET or bet > max_bet:
                messagebox.showerror("Invalid Bet", f"Bet must be between ${MIN_BET} and ${max_bet}")
                return
            self.bet = bet
            self.gambling.current_bet = bet
            self.deck = self.create_deck()
            random.shuffle(self.deck)
            self.player_hand = [self.deck.pop(), self.deck.pop()]
            self.dealer_hand = [self.deck.pop(), self.deck.pop()]
            self.show_table()
            bet_entry.config(state='disabled')
            deal_btn.config(state='disabled')

        deal_btn = tk.Button(self.window, text="Deal", command=start_hand, font=('Arial', 14), bg='#FFD369', fg='#222831')
        deal_btn.pack(pady=10)

    def create_deck(self):
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        return list(itertools.product(ranks, suits)) * 4

    def hand_value(self, hand):
        value = 0
        aces = 0
        for rank, _ in hand:
            if rank in ['J', 'Q', 'K']:
                value += 10
            elif rank == 'A':
                value += 11
                aces += 1
            else:
                value += int(rank)
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def show_table(self):
        if self.player_label:
            self.player_label.destroy()
        if self.dealer_label:
            self.dealer_label.destroy()
        self.player_label = tk.Label(self.window, text=f"Your hand: {self.format_hand(self.player_hand)} ({self.hand_value(self.player_hand)})", font=('Arial', 16), fg='#00ADB5', bg='#222831')
        self.player_label.pack(pady=10)
        self.dealer_label = tk.Label(self.window, text=f"Dealer shows: {self.format_hand([self.dealer_hand[0]])} (??)", font=('Arial', 16), fg='#FFD369', bg='#222831')
        self.dealer_label.pack(pady=10)
        if not self.hit_btn:
            self.hit_btn = tk.Button(self.window, text="Hit", command=self.hit, font=('Arial', 14), bg='#FFD369', fg='#222831')
            self.hit_btn.pack(side='left', padx=40, pady=10)
        if not self.stand_btn:
            self.stand_btn = tk.Button(self.window, text="Stand", command=self.stand, font=('Arial', 14), bg='#FFD369', fg='#222831')
            self.stand_btn.pack(side='left', padx=40, pady=10)

    def format_hand(self, hand):
        return ' '.join([f"{r}{s}" for r, s in hand])

    def hit(self):
        self.player_hand.append(self.deck.pop())
        self.player_label.config(text=f"Your hand: {self.format_hand(self.player_hand)} ({self.hand_value(self.player_hand)})")
        if self.hand_value(self.player_hand) > 21:
            self.end_hand('bust')

    def stand(self):
        self.dealer_play()

    def dealer_play(self):
        self.dealer_label.config(text=f"Dealer hand: {self.format_hand(self.dealer_hand)} ({self.hand_value(self.dealer_hand)})")
        while self.hand_value(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.pop())
            self.dealer_label.config(text=f"Dealer hand: {self.format_hand(self.dealer_hand)} ({self.hand_value(self.dealer_hand)})")
        self.end_hand('stand')

    def end_hand(self, reason):
        player_val = self.hand_value(self.player_hand)
        dealer_val = self.hand_value(self.dealer_hand)
        msg = ""
        if reason == 'bust':
            self.gambling.bankroll -= self.bet
            msg = f"You busted! -${self.bet:.2f}"
        elif dealer_val > 21 or player_val > dealer_val:
            self.gambling.bankroll += self.bet
            msg = f"You win! +${self.bet:.2f}"
        elif player_val == dealer_val:
            msg = "Push! Bet returned."
        else:
            self.gambling.bankroll -= self.bet
            msg = f"You lose! -${self.bet:.2f}"
        self.result_label.config(text=msg)
        self.bankroll_label.config(text=f"Bankroll: ${self.gambling.bankroll:.2f}")
        self.gui.update_bankroll()
        self.hit_btn.config(state='disabled')
        self.stand_btn.config(state='disabled')
        tk.Button(self.window, text="Back to Casino", command=self.window.destroy, font=('Arial', 12), bg='#393E46', fg='white').pack(pady=20)

class SlotsGame:
    def __init__(self, gui):
        self.gui = gui
        self.gambling = gui.gambling
        self.window = None
        self.animating = False

    def start(self):
        self.window = tk.Toplevel(self.gui.root)
        self.window.title("Slots")
        self.window.geometry("500x500")
        self.window.configure(bg='#222831')
        bankroll_label = tk.Label(self.window, text=f"Bankroll: ${self.gambling.bankroll:.2f}", font=('Arial', 14), fg='#FFD369', bg='#222831')
        bankroll_label.pack(pady=10)
        tk.Label(self.window, text="Place your bet:", font=('Arial', 14), fg='#EEEEEE', bg='#222831').pack(pady=5)
        bet_var = tk.DoubleVar()
        bet_entry = tk.Entry(self.window, textvariable=bet_var, font=('Arial', 12))
        bet_entry.pack(pady=5)
        result_label = tk.Label(self.window, text="", font=('Arial', 18), fg='#FFD369', bg='#222831')
        result_label.pack(pady=20)
        spin_label = tk.Label(self.window, text="🍒 🍋 🔔", font=('Arial', 32), fg='#FFD369', bg='#222831')
        spin_label.pack(pady=20)

        def play_slots():
            bet = bet_var.get()
            max_bet = min(self.gambling.bankroll, MAX_BET)
            if bet < MIN_BET or bet > max_bet:
                messagebox.showerror("Invalid Bet", f"Bet must be between ${MIN_BET} and ${max_bet}")
                return
            self.gambling.current_bet = bet
            # Animation and sound
            self.animating = True
            spin_btn.config(state='disabled')
            threading.Thread(target=self.animate_spin, args=(spin_label, result_label, bankroll_label, bet, spin_btn)).start()

        spin_btn = tk.Button(self.window, text="Spin", command=play_slots, font=('Arial', 14), bg='#FFD369', fg='#222831')
        spin_btn.pack(pady=10)
        tk.Button(self.window, text="Back to Casino", command=self.window.destroy, font=('Arial', 12), bg='#393E46', fg='white').pack(pady=20)

    def animate_spin(self, spin_label, result_label, bankroll_label, bet, spin_btn):
        symbols = ['🍒', '🍋', '🔔', '⭐', '💎', '7️⃣']
        spin = [random.choice(symbols) for _ in range(3)]
        # Play sound
        sound_path = os.path.join(os.path.dirname(__file__), "gamble.wav")
        if sys.platform == "win32" and os.path.exists(sound_path):
            winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        # Animation loop
        for i in range(15):
            temp_spin = [random.choice(symbols) for _ in range(3)]
            spin_label.config(text=' '.join(temp_spin))
            time.sleep(0.08)
        # Final result
        spin_label.config(text=' '.join(spin))
        msg = ""
        if spin[0] == spin[1] == spin[2]:
            payout = bet * 20
            self.gambling.bankroll += payout
            msg = f"Jackpot! +${payout:.2f}"
        elif len(set(spin)) == 2:
            payout = bet * 5
            self.gambling.bankroll += payout
            msg = f"Nice! +${payout:.2f}"
        elif '7️⃣' in spin:
            payout = bet * 2
            self.gambling.bankroll += payout
            msg = f"Lucky Seven! +${payout:.2f}"
        else:
            self.gambling.bankroll -= bet
            msg = f"You lose! -${bet:.2f}"
        result_label.config(text=msg)
        bankroll_label.config(text=f"Bankroll: ${self.gambling.bankroll:.2f}")
        self.gui.update_bankroll()
        spin_btn.config(state='normal')
        self.animating = False

# --- MODERN CASINO GUI ---
class CasinoGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎰 Casino Royale 🎰")
        self.root.geometry("900x700")
        self.root.configure(bg='#222831')
        self.gambling = GamblingSystem()
        self.setup_lobby()

    def setup_lobby(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        # Casino Title
        tk.Label(self.root, text="🎰 CASINO ROYALE 🎰", font=('Arial', 32, 'bold'), fg='#FFD369', bg='#222831').pack(pady=40)
        # Bankroll
        self.bankroll_label = tk.Label(self.root, text=f"Bankroll: ${self.gambling.bankroll:.2f}", font=('Arial', 18), fg='#00ADB5', bg='#222831')
        self.bankroll_label.pack(pady=10)
        # Games Frame
        games_frame = tk.Frame(self.root, bg='#222831')
        games_frame.pack(pady=40)
        # Minesweeper
        tk.Button(games_frame, text="💣 Minesweeper", command=self.start_minesweeper, font=('Arial', 18), bg='#393E46', fg='white', width=20, height=2).grid(row=0, column=0, padx=20, pady=10)
        # Blackjack
        tk.Button(games_frame, text="🃏 Blackjack", command=self.start_blackjack, font=('Arial', 18), bg='#393E46', fg='white', width=20, height=2).grid(row=0, column=1, padx=20, pady=10)
        # Slots
        tk.Button(games_frame, text="🎰 Slots", command=self.start_slots, font=('Arial', 18), bg='#393E46', fg='white', width=20, height=2).grid(row=1, column=1, padx=20, pady=10)
        # Poker button removed
        # Rules
        tk.Button(self.root, text="📋 Casino Rules", command=self.show_rules, font=('Arial', 14), bg='#FFD369', fg='#222831', width=20, height=2).pack(pady=10)
        # Exit
        tk.Button(self.root, text="❌ Exit Casino", command=self.root.quit, font=('Arial', 14), bg='#393E46', fg='white', width=20, height=2).pack(pady=10)

    def update_bankroll(self):
        self.bankroll_label.config(text=f"Bankroll: ${self.gambling.bankroll:.2f}")

    def start_minesweeper(self):
        MinesweeperGamblingGUI(self)

    def start_blackjack(self):
        BlackjackGame(self).start()

    def start_slots(self):
        SlotsGame(self).start()

    # Poker game removed

    def show_rules(self):
        rules_text = (
            "MINESWEEPER GAMBLING RULES:\n\n"
            "🎯 Objective: Reveal all safe cells without hitting mines\n"
            "💰 Betting: Place bets from $1 to $1000\n"
            "🎲 Difficulties:\n"
            "  • Easy: 9×9 grid, 10 mines, 1.5× multiplier\n"
            "  • Medium: 16×16 grid, 40 mines, 2.0× multiplier\n"
            "  • Hard: 16×30 grid, 99 mines, 2.5× multiplier\n\n"
            "🎮 Controls:\n"
            "  • Left click: Reveal cell\n"
            "  • Right click: Flag/unflag cell\n"
            "  • Win: Get payout based on difficulty\n"
            "  • Lose: Lose bet amount\n\n"
            "💡 Tips:\n"
            "  • Numbers show adjacent mine count\n"
            "  • Use flags to mark suspected mines\n"
            "  • First click is always safe"
        )
        messagebox.showinfo("Game Rules", rules_text)

# --- MINESWEEPER GUI (refactored to work with CasinoGUI) ---
class MinesweeperGamblingGUI:
    def __init__(self, casino_gui):
        self.casino_gui = casino_gui
        self.root = casino_gui.root
        self.gambling = casino_gui.gambling
        self.game = None
        self.buttons = []
        self.difficulty = 'easy'
        self.setup_main_menu()

    def setup_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text="💣 MINESWEEPER 💣", font=('Arial', 28, 'bold'), fg='#00ADB5', bg='#222831').pack(pady=30)
        self.bankroll_label = tk.Label(self.root, text=f"Bankroll: ${self.gambling.bankroll:.2f}", font=('Arial', 16), fg='#FFD369', bg='#222831')
        self.bankroll_label.pack(pady=10)
        button_frame = tk.Frame(self.root, bg='#222831')
        button_frame.pack(pady=30)
        tk.Button(button_frame, text="🎮 New Game", command=self.new_game, font=('Arial', 14), bg='#393E46', fg='white', width=20, height=2).pack(pady=10)
        tk.Button(button_frame, text="🏠 Casino Lobby", command=self.casino_gui.setup_lobby, font=('Arial', 14), bg='#FFD369', fg='#222831', width=20, height=2).pack(pady=10)
        tk.Button(button_frame, text="📋 Rules", command=self.show_rules, font=('Arial', 14), bg='#00ADB5', fg='white', width=20, height=2).pack(pady=10)

    def new_game(self):
        """Start new game"""
        if self.gambling.bankroll < 1:
            messagebox.showerror("Insufficient Funds", 
                                 "You don't have enough money to play!")
            return
        
        # Difficulty selection
        difficulty_window = tk.Toplevel(self.root)
        difficulty_window.title("Select Difficulty")
        difficulty_window.geometry("300x250")
        difficulty_window.configure(bg='#34495E')
        
        tk.Label(difficulty_window, text="Choose Difficulty:", 
                font=('Arial', 14), fg='white', bg='#34495E').pack(pady=10)
        
        difficulty_var = tk.StringVar(value='easy')
        for diff in DIFFICULTIES.keys():
            tk.Radiobutton(difficulty_window, 
                          text=f"{diff.title()} - {DIFFICULTIES[diff]['mines']} mines", 
                          variable=difficulty_var, value=diff,
                          font=('Arial', 12), bg='#34495E', fg='white',
                          selectcolor='#2C3E50').pack(anchor='w', padx=20)
        
        def confirm_difficulty():
            self.difficulty = difficulty_var.get()
            difficulty_window.destroy()
            self.get_bet_amount()
        
        tk.Button(difficulty_window, text="Next", command=confirm_difficulty,
                 font=('Arial', 12), bg='#3498DB', fg='white').pack(pady=20)
    
    def get_bet_amount(self):
        """Get bet amount"""
        bet_window = tk.Toplevel(self.root)
        bet_window.title("Place Your Bet")
        bet_window.geometry("300x200")
        bet_window.configure(bg='#34495E')
        
        tk.Label(bet_window, text=f"Bankroll: ${self.gambling.bankroll:.2f}", 
                font=('Arial', 12), fg='white', bg='#34495E').pack(pady=10)
        
        tk.Label(bet_window, text="Enter bet amount:", 
                font=('Arial', 12), fg='white', bg='#34495E').pack(pady=5)
        
        bet_var = tk.DoubleVar()
        bet_entry = tk.Entry(bet_window, textvariable=bet_var, font=('Arial', 12))
        bet_entry.pack(pady=5)
        
        def confirm_bet():
            bet = bet_var.get()
            max_bet = min(self.gambling.bankroll, MAX_BET)
            if MIN_BET <= bet <= max_bet:
                self.gambling.place_bet(bet, self.difficulty)
                bet_window.destroy()
                self.start_game()
            else:
                messagebox.showerror("Invalid Bet", 
                                   f"Bet must be between ${MIN_BET} and ${max_bet}")
        
        tk.Button(bet_window, text="Start Game", command=confirm_bet,
                 font=('Arial', 12), bg='#2ECC71', fg='white').pack(pady=20)
    
    def start_game(self):
        """Start the game"""
        self.game = MinesweeperGame(self.difficulty)
        
        # Create game window
        self.game_window = tk.Toplevel(self.root)
        self.game_window.title(f"Minesweeper - {self.difficulty.title()} - Bet: ${self.gambling.current_bet}")
        self.game_window.configure(bg='#2C3E50')
        
        # Game info
        info_frame = tk.Frame(self.game_window, bg='#2C3E50')
        info_frame.pack(fill='x', padx=10, pady=10)
        
        self.game_bankroll_label = tk.Label(info_frame, text=f"Bankroll: ${self.gambling.bankroll:.2f}", 
                                          font=('Arial', 12), fg='#2ECC71', bg='#2C3E50')
        self.game_bankroll_label.pack(side='left')
        
        self.game_bet_label = tk.Label(info_frame, text=f"Bet: ${self.gambling.current_bet}", 
                                     font=('Arial', 12), fg='#F39C12', bg='#2C3E50')
        self.game_bet_label.pack(side='left', padx=20)
        
        # Game board
        board_frame = tk.Frame(self.game_window, bg='#2C3E50')
        board_frame.pack(padx=10, pady=10)
        
        self.buttons = []
        rows = self.game.rows
        cols = self.game.cols
        
        for r in range(rows):
            button_row = []
            for c in range(cols):
                btn = tk.Button(board_frame, text=' ', width=2, height=1,
                              font=('Arial', 10, 'bold'), bg='#BDC3C7', fg='black')
                btn.grid(row=r, column=c, padx=1, pady=1)
                btn.bind('<Button-1>', lambda e, row=r, col=c: self.left_click(row, col))
                btn.bind('<Button-3>', lambda e, row=r, col=c: self.right_click(row, col))
                button_row.append(btn)
            self.buttons.append(button_row)
        
        # Control buttons
        control_frame = tk.Frame(self.game_window, bg='#2C3E50')
        control_frame.pack(fill='x', padx=10, pady=10)
        
        restart_btn = tk.Button(control_frame, text="🔄 Restart", command=self.restart_game,
                              font=('Arial', 10), bg='#3498DB', fg='white')
        restart_btn.pack(side='left', padx=5)
        
        quit_btn = tk.Button(control_frame, text="🏠 Main Menu", command=self.game_window.destroy,
                           font=('Arial', 10), bg='#E74C3C', fg='white')
        quit_btn.pack(side='right', padx=5)
    
    def left_click(self, row, col):
        """Handle left click"""
        if not self.game or self.game.is_game_over():
            return
        
        self.game.reveal_cell(row, col)
        self.update_display()
        
        if self.game.is_game_over():
            self.handle_game_end()
    
    def right_click(self, row, col):
        """Handle right click"""
        if not self.game or self.game.is_game_over():
            return
        
        self.game.toggle_flag(row, col)
        self.update_display()
    
    def update_display(self):
        """Update display"""
        if not self.game:
            return
        
        for r in range(self.game.rows):
            for c in range(self.game.cols):
                btn = self.buttons[r][c]
                
                if self.game.flagged[r][c]:
                    btn.config(text='🚩', bg='#E74C3C', fg='white')
                elif self.game.revealed[r][c]:
                    if self.game.board[r][c] == -1:
                        btn.config(text='💣', bg='#E74C3C', fg='white')
                    elif self.game.board[r][c] == 0:
                        btn.config(text='', bg='#ECF0F1')
                    else:
                        colors = {1: '#3498DB', 2: '#2ECC71', 3: '#E74C3C', 
                                4: '#9B59B6', 5: '#F39C12', 6: '#1ABC9C', 
                                7: '#34495E', 8: '#95A5A6'}
                        color = colors.get(self.game.board[r][c], '#000000')
                        btn.config(text=str(self.game.board[r][c]), bg='#ECF0F1', fg=color)
                else:
                    btn.config(text='', bg='#BDC3C7')
    
    def handle_game_end(self):
        """Handle game completion"""
        if self.game.is_game_won():
            result = self.gambling.win_game()
            messagebox.showinfo("🎉 You Won!", 
                              f"Congratulations! You won ${result['payout']:.2f}\n"
                              f"New bankroll: ${result['new_bankroll']:.2f}")
        else:
            result = self.gambling.lose_game()
            messagebox.showinfo("💥 Game Over", 
                              f"You hit a mine! Lost ${result['loss']:.2f}\n"
                              f"New bankroll: ${result['new_bankroll']:.2f}")
        self.bankroll_label.config(text=f"Bankroll: ${self.gambling.bankroll:.2f}")
        self.casino_gui.update_bankroll()

    def show_rules(self):
        """Show game rules"""
        rules_text = (
            "MINESWEEPER GAMBLING RULES:\n\n"
            "🎯 Objective: Reveal all safe cells without hitting mines\n"
            "💰 Betting: Place bets from $1 to $1000\n"
            "🎲 Difficulties:\n"
            "  • Easy: 9×9 grid, 10 mines, 1.5× multiplier\n"
            "  • Medium: 16×16 grid, 40 mines, 2.0× multiplier\n"
            "  • Hard: 16×30 grid, 99 mines, 2.5× multiplier\n\n"
            "🎮 Controls:\n"
            "  • Left click: Reveal cell\n"
            "  • Right click: Flag/unflag cell\n"
            "  • Win: Get payout based on difficulty\n"
            "  • Lose: Lose bet amount\n\n"
            "💡 Tips:\n"
            "  • Numbers show adjacent mine count\n"
            "  • Use flags to mark suspected mines\n"
            "  • First click is always safe"
        )
        messagebox.showinfo("Game Rules", rules_text)

if __name__ == "__main__":
    app = CasinoGUI()
    app.root.mainloop()
    # Compile this file to .pyc after running:
    import compileall, os
    compileall.compile_file(os.path.abspath(__file__), force=True)
    if hasattr(sys, 'frozen'):
        pass
    else:
        compileall.compile_file(os.path.abspath(__file__), force=True)
        compileall.compile_file(os.path.abspath(__file__), force=True)
        self.game.reveal_cell(row, col)
        self.update_display()
        
        if self.game.is_game_over():
            self.handle_game_end()
    
    def right_click(self, row, col):
        """Handle right click"""
        if not self.game or self.game.is_game_over():
            return
        
        self.game.toggle_flag(row, col)
        self.update_display()
    
    def update_display(self):
        """Update display"""
        if not self.game:
            return
        
        for r in range(self.game.rows):
            for c in range(self.game.cols):
                btn = self.buttons[r][c]
                
                if self.game.flagged[r][c]:
                    btn.config(text='🚩', bg='#E74C3C', fg='white')
                elif self.game.revealed[r][c]:
                    if self.game.board[r][c] == -1:
                        btn.config(text='💣', bg='#E74C3C', fg='white')
                    elif self.game.board[r][c] == 0:
                        btn.config(text='', bg='#ECF0F1')
                    else:
                        colors = {1: '#3498DB', 2: '#2ECC71', 3: '#E74C3C', 
                                4: '#9B59B6', 5: '#F39C12', 6: '#1ABC9C', 
                                7: '#34495E', 8: '#95A5A6'}
                        color = colors.get(self.game.board[r][c], '#000000')
                        btn.config(text=str(self.game.board[r][c]), bg='#ECF0F1', fg=color)
                else:
                    btn.config(text='', bg='#BDC3C7')
    
    def handle_game_end(self):
        """Handle game completion"""
        if self.game.is_game_won():
            result = self.gambling.win_game()
            messagebox.showinfo("🎉 You Won!", 
                              f"Congratulations! You won ${result['payout']:.2f}\n"
                              f"New bankroll: ${result['new_bankroll']:.2f}")
        else:
            result = self.gambling.lose_game()
            messagebox.showinfo("💥 Game Over", 
                              f"You hit a mine! Lost ${result['loss']:.2f}\n"
                              f"New bankroll: ${result['new_bankroll']:.2f}")
        self.bankroll_label.config(text=f"Bankroll: ${self.gambling.bankroll:.2f}")
        self.casino_gui.update_bankroll()

    def show_rules(self):
        """Show game rules"""
        rules_text = (
            "MINESWEEPER GAMBLING RULES:\n\n"
            "🎯 Objective: Reveal all safe cells without hitting mines\n"
            "💰 Betting: Place bets from $1 to $1000\n"
            "🎲 Difficulties:\n"
            "  • Easy: 9×9 grid, 10 mines, 1.5× multiplier\n"
            "  • Medium: 16×16 grid, 40 mines, 2.0× multiplier\n"
            "  • Hard: 16×30 grid, 99 mines, 2.5× multiplier\n\n"
            "🎮 Controls:\n"
            "  • Left click: Reveal cell\n"
            "  • Right click: Flag/unflag cell\n"
            "  • Win: Get payout based on difficulty\n"
            "  • Lose: Lose bet amount\n\n"
            "💡 Tips:\n"
            "  • Numbers show adjacent mine count\n"
            "  • Use flags to mark suspected mines\n"
            "  • First click is always safe"
        )
        messagebox.showinfo("Game Rules", rules_text)

if __name__ == "__main__":
    app = CasinoGUI()
    app.root.mainloop()



    # Compile this file to .pyc after running:
    import compileall, os
    compileall.compile_file(os.path.abspath(__file__), force=True)
    if hasattr(sys, 'frozen'):
        pass
    else:
        compileall.compile_file(os.path.abspath(__file__), force=True)
        compileall.compile_file(os.path.abspath(__file__), force=True)
        self.game.reveal_cell(row, col)
        self.update_display()
        
        if self.game.is_game_over():
            self.handle_game_end()
    
    def right_click(self, row, col):
        """Handle right click"""
        if not self.game or self.game.is_game_over():
            return
        
        self.game.toggle_flag(row, col)
        self.update_display()
    
    def update_display(self):
        """Update display"""
        if not self.game:
            return
        
        for r in range(self.game.rows):
            for c in range(self.game.cols):
                btn = self.buttons[r][c]
                
                if self.game.flagged[r][c]:
                    btn.config(text='🚩', bg='#E74C3C', fg='white')
                elif self.game.revealed[r][c]:
                    if self.game.board[r][c] == -1:
                        btn.config(text='💣', bg='#E74C3C', fg='white')
                    elif self.game.board[r][c] == 0:
                        btn.config(text='', bg='#ECF0F1')
                    else:
                        colors = {1: '#3498DB', 2: '#2ECC71', 3: '#E74C3C', 
                                4: '#9B59B6', 5: '#F39C12', 6: '#1ABC9C', 
                                7: '#34495E', 8: '#95A5A6'}
                        color = colors.get(self.game.board[r][c], '#000000')
                        btn.config(text=str(self.game.board[r][c]), bg='#ECF0F1', fg=color)
                else:
                    btn.config(text='', bg='#BDC3C7')
    
    def handle_game_end(self):
        """Handle game completion"""
        if self.game.is_game_won():
            result = self.gambling.win_game()
            messagebox.showinfo("🎉 You Won!", 
                              f"Congratulations! You won ${result['payout']:.2f}\n"
                              f"New bankroll: ${result['new_bankroll']:.2f}")
        else:
            result = self.gambling.lose_game()
            messagebox.showinfo("💥 Game Over", 
                              f"You hit a mine! Lost ${result['loss']:.2f}\n"
                              f"New bankroll: ${result['new_bankroll']:.2f}")
        self.bankroll_label.config(text=f"Bankroll: ${self.gambling.bankroll:.2f}")
        self.casino_gui.update_bankroll()

    def show_rules(self):
        """Show game rules"""
        rules_text = (
            "MINESWEEPER GAMBLING RULES:\n\n"
            "🎯 Objective: Reveal all safe cells without hitting mines\n"
            "💰 Betting: Place bets from $1 to $1000\n"
            "🎲 Difficulties:\n"
            "  • Easy: 9×9 grid, 10 mines, 1.5× multiplier\n"
            "  • Medium: 16×16 grid, 40 mines, 2.0× multiplier\n"
            "  • Hard: 16×30 grid, 99 mines, 2.5× multiplier\n\n"
            "🎮 Controls:\n"
            "  • Left click: Reveal cell\n"
            "  • Right click: Flag/unflag cell\n"
            "  • Win: Get payout based on difficulty\n"
            "  • Lose: Lose bet amount\n\n"
            "💡 Tips:\n"
            "  • Numbers show adjacent mine count\n"
            "  • Use flags to mark suspected mines\n"
            "  • First click is always safe"
        )
        messagebox.showinfo("Game Rules", rules_text)

if __name__ == "__main__":
    app = CasinoGUI()
    app.root.mainloop()
