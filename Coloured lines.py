from tkinter import messagebox
import tkinter as tk
import random
import pygame
from collections import deque
import os

# --- File path to save high scores ---
SCORE_FILE = "high_scores.txt"
if not os.path.exists(SCORE_FILE):
    with open(SCORE_FILE, 'w') as f:
        pass

# Initialize sound
pygame.mixer.init()
try:
    move_sound = pygame.mixer.Sound("audio1.wav")
    clear_sound = pygame.mixer.Sound("audio1.wav.mp3")
except:
    move_sound = None
    clear_sound = None

try:
    pygame.mixer.music.load("C:\\Users\\24wh1\\OneDrive\\Desktop\\soumya\\roblox-minecraft-fortnite-video-game-music-358426.mp3")
except pygame.error as e:
    print("Music load error:", e)

ROWS, COLS = 9, 9
CELL_SIZE = 60
BALL_COLORS = ["red", "green", "blue", "yellow", "purple", "orange", "cyan"]
NEW_BALLS = 3

grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
score = 0
high_score = 0
selected = None
player_name = ""
canvas = None
game_window = None  # <-- Added to track game window for resume/play again

def create_gradient_background(canvas, width, height, color1="#1e3c72", color2="#2a5298"):
    canvas.delete("gradient")
    for i in range(height):
        ratio = i / height
        r = int(int(color1[1:3], 16) + (int(color2[1:3], 16) - int(color1[1:3], 16)) * ratio)
        g = int(int(color1[3:5], 16) + (int(color2[3:5], 16) - int(color1[3:5], 16)) * ratio)
        b = int(int(color1[5:7], 16) + (int(color2[5:7], 16) - int(color1[5:7], 16)) * ratio)
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_line(0, i, width, i, fill=color, tags="gradient")

def create_animated_background(window):
    bg_canvas = tk.Canvas(window, highlightthickness=0)
    bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
    window.update()
    width, height = window.winfo_width(), window.winfo_height()
    create_gradient_background(bg_canvas, width, height, "#0f0c29", "#24243e")
    particles = []
    colors = ["#ffffff", "#ffeb3b", "#e91e63", "#9c27b0", "#2196f3", "#00bcd4", "#4caf50"]
    for _ in range(50):
        x, y = random.randint(0, width), random.randint(0, height)
        size, color, speed = random.randint(2, 8), random.choice(colors), random.uniform(0.5, 2.0)
        p = bg_canvas.create_oval(x-size//2, y-size//2, x+size//2, y+size//2, fill=color, outline="")
        particles.append({'id': p, 'x': x, 'y': y, 'speed': speed, 'size': size})
    def animate():
        for p in particles:
            p['y'] += p['speed']
            if p['y'] > height + p['size']:
                p['y'], p['x'] = -p['size'], random.randint(0, width)
            bg_canvas.coords(p['id'], p['x'] - p['size']//2, p['y'] - p['size']//2,
                             p['x'] + p['size']//2, p['y'] + p['size']//2)
        window.after(50, animate)
    animate()
    return bg_canvas

def save_score(name, score):
    scores = load_scores()
    scores.append((name, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    with open(SCORE_FILE, 'w') as f:
        for name, score in scores[:10]:
            f.write(f"{name}:{score}\n")
    return scores[:10]

def load_scores():
    scores = []
    try:
        with open(SCORE_FILE, 'r') as f:
            for line in f:
                if ":" in line:
                    name, score = line.strip().split(":")
                    scores.append((name, int(score)))
    except:
        pass
    return scores

def load_high_score():
    scores = load_scores()
    return scores[0][1] if scores else 0

def load_leaderboard():
    return load_scores()[:10]

def show_title_screen():
    try:
        pygame.mixer.music.play(-1)
    except:
        pass
    def on_start():
        global player_name
        player_name = name_entry.get().strip() or "Player"
        try:
            pygame.mixer.music.stop()
        except:
            pass
        title_win.destroy()
        start_game_window(player_name)

    title_win = tk.Tk()
    title_win.attributes('-fullscreen', True)
    title_win.configure(bg="black")
    title_win.title("Colored Lines - Welcome")
    create_animated_background(title_win)

    main_frame = tk.Frame(title_win, bg="#1a1a2e")
    main_frame.place(relx=0.5, rely=0.5, anchor="center")
    title_text = "COLORED LINES"
    colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4", "#feca57", "#ff9ff3", "#54a0ff"]
    title_frame = tk.Frame(main_frame, bg="#1a1a2e")
    title_frame.pack(pady=30)
    for i, (letter, color) in enumerate(zip(title_text, colors * 2)):
        label = tk.Label(title_frame, text=letter, font=("Arial Black", 48, "bold"), fg=color, bg="#1a1a2e")
        label.pack(side=tk.LEFT, padx=2)
        def animate_glow(lbl, delay=i*100):
            def glow():
                current = lbl.cget("fg")
                lbl.configure(fg="#ffffff" if current == color else color)
                title_win.after(1000 + delay, glow)
            title_win.after(delay, glow)
        animate_glow(label)

    rules_text = (
        "\n🎮 GAME DESCRIPTION 🎮\n"
        "Colored Lines is a strategic puzzle game on a 9×9 grid.\n\n"
        "🎯 HOW TO PLAY:\n"
        "• Click a ball, then click an empty cell to move it\n"
        "• Make lines of 5+ same-colored balls to clear them\n"
        "• You earn 2 points per ball cleared\n"
        "• 3 new balls appear if you don't clear a line\n"
        "• Game ends when the board is full\n\n"
        "🏆 STRATEGY TIPS:\n"
        "• Plan ahead for chain clears\n"
        "• Leave room to maneuver\n"
        "• Clear multiple lines at once for more points!\n"
    )
    tk.Label(main_frame, text=rules_text, font=("Segoe UI", 14), fg="#e8eaf6", bg="#1a1a2e").pack(pady=10)

    name_entry = tk.Entry(main_frame, font=("Arial", 16), width=25, bg="#2c2c54", fg="white")
    name_entry.pack(pady=10)
    name_entry.focus()
    start_btn = tk.Button(main_frame, text="🚀 START GAME", font=("Arial", 18, "bold"), 
                          bg="#ff6b6b", fg="white", command=on_start)
    start_btn.pack(pady=20)
    name_entry.bind("<Return>", lambda e: on_start())
    title_win.mainloop()

def draw_grid(canvas):
    canvas.delete("all")
    create_gradient_background(canvas, COLS*CELL_SIZE, ROWS*CELL_SIZE, "#667eea", "#764ba2")
    for r in range(ROWS):
        for c in range(COLS):
            x1, y1, x2, y2 = c*CELL_SIZE, r*CELL_SIZE, (c+1)*CELL_SIZE, (r+1)*CELL_SIZE
            canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, outline="#ffffff", width=2)
            color = grid[r][c]
            if color:
                canvas.create_oval(x1+6, y1+6, x2-6, y2-6, fill=color, outline="white", width=2)
    if selected:
        r, c = selected
        x1, y1, x2, y2 = c*CELL_SIZE, r*CELL_SIZE, (c+1)*CELL_SIZE, (r+1)*CELL_SIZE
        canvas.create_rectangle(x1+1, y1+1, x2-1, y2-1, outline="#ffd700", width=4)

def is_path_clear(start, end):
    visited = [[False]*COLS for _ in range(ROWS)]
    queue = deque([start])
    visited[start[0]][start[1]] = True
    while queue:
        r, c = queue.popleft()
        if (r, c) == end:
            return True
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if 0<=nr<ROWS and 0<=nc<COLS and not visited[nr][nc] and not grid[nr][nc]:
                visited[nr][nc] = True
                queue.append((nr, nc))
    return False

def clear_lines():
    cleared, to_clear = 0, set()
    def check(line):
        count = 1
        for i in range(1, len(line)):
            r1, c1 = line[i-1]
            r2, c2 = line[i]
            if grid[r1][c1] == grid[r2][c2] and grid[r1][c1]:
                count += 1
            else:
                if count >= 5:
                    to_clear.update(line[i-count:i])
                count = 1
        if count >= 5:
            to_clear.update(line[-count:])
    for r in range(ROWS): check([(r, c) for c in range(COLS)])
    for c in range(COLS): check([(r, c) for r in range(ROWS)])
    for d in range(-ROWS+1, COLS):
        check([(r, r - d) for r in range(ROWS) if 0 <= r - d < COLS])
        check([(r, d - r) for r in range(ROWS) if 0 <= d - r < COLS])
    for r, c in to_clear: grid[r][c] = None
    if to_clear and clear_sound: clear_sound.play()
    return len(to_clear)

def add_new_balls(n):
    empty = [(r, c) for r in range(ROWS) for c in range(COLS) if not grid[r][c]]
    random.shuffle(empty)
    for _ in range(min(n, len(empty))):
        r, c = empty.pop()
        grid[r][c] = random.choice(BALL_COLORS)

def on_canvas_click(event):
    global selected, score, high_score
    col, row = event.x // CELL_SIZE, event.y // CELL_SIZE
    if not (0 <= row < ROWS and 0 <= col < COLS): return
    if selected:
        sr, sc = selected
        if grid[sr][sc] and not grid[row][col] and is_path_clear((sr, sc), (row, col)):
            grid[row][col], grid[sr][sc] = grid[sr][sc], None
            selected = None
            if move_sound: move_sound.play()
            cleared = clear_lines()
            draw_grid(canvas)
            if cleared == 0:
                add_new_balls(NEW_BALLS)
                cleared = clear_lines()
                draw_grid(canvas)
            score += cleared * 2
            score_label.config(text=f"Score: {score}")
            if score > high_score:
                high_score = score
                high_score_label.config(text=f"High Score: {high_score}")
            if all(grid[r][c] for r in range(ROWS) for c in range(COLS)):
                show_game_over(game_window)
        else:
            selected = (row, col)
            draw_grid(canvas)
    else:
        if grid[row][col]:
            selected = (row, col)
            draw_grid(canvas)

def play_again():
    global game_window
    if game_window:
        game_window.destroy()
    start_game_window(player_name)

def resume_game():
    global game_window
    if game_window:
        game_window.deiconify()
        
def show_game_over(root):
    save_score(player_name, score)
    top_scores = load_leaderboard()
    iq_level = "🧠 Genius" if score > 200 else "🎓 Smart" if score > 100 else "📚 Learner"
    end_win = tk.Toplevel(root)
    end_win.attributes('-fullscreen', True)
    end_win.configure(bg="black")
    create_animated_background(end_win)
    content = tk.Frame(end_win, bg="#1a1a2e")
    content.place(relx=0.5, rely=0.5, anchor="center")
    tk.Label(content, text="🎮 GAME OVER 🎮", font=("Arial", 32, "bold"), fg="#ff6b6b", bg="#1a1a2e").pack(pady=20)
    tk.Label(content, text=f"Final Score: {score}", font=("Arial", 24), fg="#4ecdc4", bg="#1a1a2e").pack(pady=10)
    tk.Label(content, text=f"Level: {iq_level}", font=("Arial", 20), fg="#feca57", bg="#1a1a2e").pack(pady=10)
    for i, (name, val) in enumerate(top_scores):
        color = ["#ffd700", "#c0c0c0", "#cd7f32"][i] if i < 3 else "#ffffff"
        tk.Label(content, text=f"{i+1}. {name}: {val}", font=("Arial", 14), fg=color, bg="#1a1a2e").pack()

    btn_frame = tk.Frame(content, bg="#1a1a2e")
    btn_frame.pack(pady=30)
    tk.Button(btn_frame, text="🔁 Play Again", font=("Arial", 14, "bold"), bg="#54a0ff", fg="white",
              command=lambda: [end_win.destroy(), play_again()]).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="🚪 Exit Game", font=("Arial", 14, "bold"), bg="#ff6b6b", fg="white",
              command=lambda: [end_win.destroy(), root.destroy()]).pack(side=tk.LEFT, padx=10)

def start_game_window(name):
    global player_name, score, high_score, grid, selected, score_label, high_score_label, canvas, game_window
    player_name = name
    score = 0
    high_score = load_high_score()
    grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
    selected = None

    game_window = tk.Tk()
    game_window.attributes("-fullscreen", True)
    game_window.configure(bg="black")
    game_window.title("Colored Lines - Game")
    create_animated_background(game_window)

    game_frame = tk.Frame(game_window, bg="#1a1a2e")
    game_frame.pack(pady=20)
    canvas = tk.Canvas(game_frame, width=COLS*CELL_SIZE, height=ROWS*CELL_SIZE, bg="lightgrey")
    canvas.pack(pady=20, padx=20)
    canvas.bind("<Button-1>", on_canvas_click)

    ui = tk.Frame(game_window, bg="#16213e")
    ui.pack(pady=10)
    score_label = tk.Label(ui, text="Score: 0", font=("Arial", 18, "bold"), fg="#4ecdc4", bg="#16213e")
    score_label.pack(side=tk.LEFT, padx=30)
    high_score_label = tk.Label(ui, text=f"High Score: {high_score} ({player_name})", font=("Arial", 18, "bold"), fg="#feca57", bg="#16213e")
    high_score_label.pack(side=tk.LEFT, padx=30)
    tk.Label(ui, text=f"Player: {player_name}", font=("Arial", 16), fg="#ff9ff3", bg="#16213e").pack(side=tk.LEFT, padx=30)

    control_frame = tk.Frame(ui, bg="#16213e")
    control_frame.pack(side=tk.RIGHT, padx=20)

    def confirm_exit():
        if messagebox.askyesno("Exit", "Do you want to exit the game?"):
            game_window.destroy()

    tk.Button(control_frame, text="🔁 Play Again", font=("Arial", 14), bg="#54a0ff", fg="white", command=play_again).pack(side=tk.LEFT, padx=5)
    tk.Button(control_frame, text="🚪 Exit", font=("Arial", 14, "bold"), bg="#ff6b6b", fg="white", command=confirm_exit).pack(side=tk.LEFT, padx=5)

    add_new_balls(NEW_BALLS)
    draw_grid(canvas)
    game_window.mainloop()


def start_game(name):
    start_game_window(name)

# --- Start the Game ---
show_title_screen()