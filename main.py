# camle.py

import pygame
import sys
import random
from pygame.locals import *

# 語言設定
language = 'zh-TW'  # 預設語言為中文

# 定義語言資源
languages = {
    'zh-TW': {
        'game_over': "遊戲結束",
        'final_score': "最終得分：{score}",
        'restart': "重新開始",
        'quit': "退出",
        'play': "開始",
        'language': "語言",
        'credits': "版權",
        'main_menu_title': 'Gibbon Jump',
        'start_game': '開始遊戲 (左鍵或觸控)',
        'language_option': '語言選擇',
        'credits_option': '版權資訊',
        'language_title': '選擇語言',
        'back': '返回主選單',
        'toggle_language': "語言已切換為 {lang}",
        'difficulty_level': '難度等級: {difficulty}',
        'score': '分數: {score}',
        'energy': '能量: {energy}',
        'lives': '生命值: {lives}',
        'volume_music': '音樂音量',
        'volume_sound': '音效音量',
        'paused': '遊戲已暫停',
        'touch_to_start': '觸控以開始遊戲',
        'language_switch': '切換語言',
        'select_language': '選擇語言',
        'english': 'English',
        'chinese': '中文',
        'credits_text': (
            "背景音樂: Quinn Fisher Gourmet Race(8bit remix)\n"
            "跳躍音效: opengameart.org\n"
            "碰撞音效: opengameart.org\n"
            "圖片 @BigNineNine\n"
            "文字 Noto Sans TC"
        ),
    },
    'en': {
        'game_over': "Game Over",
        'final_score': "Final Score: {score}",
        'restart': "Restart",
        'quit': "Quit",
        'play': "Start",
        'language': "Language",
        'credits': "Credits",
        'main_menu_title': 'Gibbon Jump',
        'start_game': 'Start Game (Left Click or Touch)',
        'language_option': 'Language Selection',
        'credits_option': 'Credits Information',
        'language_title': 'Select Language',
        'back': 'Return to Main Menu',
        'toggle_language': "Language switched to {lang}",
        'difficulty_level': 'Difficulty Level: {difficulty}',
        'score': 'Score: {score}',
        'energy': 'Energy: {energy}',
        'lives': 'Lives: {lives}',
        'volume_music': 'Music Volume',
        'volume_sound': 'Sound Volume',
        'paused': 'Game Paused',
        'touch_to_start': 'Touch to start game',
        'language_switch': 'Switch Language',
        'select_language': 'Select Language',
        'english': 'English',
        'chinese': '中文',
        'credits_text': (
            "Background Music: Quinn Fisher Gourmet Race(8bit remix)\n"
            "Jump Sound Effect: opengameart.org\n"
            "Collision Sound Effect: opengameart.org\n"
            "Images @BigNineNine\n"
            "Fonts Noto Sans TC"
        ),
    }
}

def set_language(target_lang):
    """設定遊戲語言"""
    global language
    if target_lang in languages:
        language = target_lang
        lang_display = languages[language]['english'] if language == 'en' else languages[language]['chinese']
        print(languages[language]['toggle_language'].format(lang=lang_display))

# 初始化變數
WIDTH, HEIGHT = 1024, 600
GIBBON_INITIAL_Y = HEIGHT * 0.7
GIBBON_X = WIDTH * 0.1
gibbon_y = GIBBON_INITIAL_Y
gibbon_speed = 0
GRAVITY = 0.5
JUMP_SPEED = -15
is_jumping = False
energy = 0
ENERGY_CHARGE_TIME = 200
lives = 3
MAX_LIVES = 5
score = 0
difficulty_level = 1
next_difficulty_score = 10

camel_x = WIDTH
camel_y = HEIGHT * 0.7
camel_speed = 5
camel_direction = 1  # 1 表示向下，-1 表示向上
camel_speed_y = 3
camel_vertical_min_y = HEIGHT * 0.5
camel_vertical_max_y = HEIGHT * 0.7

paused = False

# 音量設定
music_volume = 0.5
sound_volume = 0.5

# 初始化 pygame
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Gibbon Jump')
clock = pygame.time.Clock()

# 加載字體
font_path = 'fonts/NotoSansTC.ttf'
font_size = 35
try:
    font = pygame.font.Font(font_path, font_size)
except FileNotFoundError:
    print(f"字體檔案未找到：{font_path}，將使用系統默認字體。")
    font = pygame.font.Font(None, font_size)

# 加載圖像並調整大小
def load_image(filename, size, fallback_color):
    """加載並調整圖像大小"""
    path = 'pic/' + filename
    try:
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, size)
        return image
    except pygame.error as e:
        print(f"Error loading {filename}: {e}")
        image = pygame.Surface(size)
        image.fill(fallback_color)
        return image

camel = load_image('camel.png', (HEIGHT // 5, HEIGHT // 5), (139, 69, 19))
gibbon = load_image('gibbon.png', (88, 146), (0, 0, 0))
background = load_image('background.png', (WIDTH, HEIGHT), (135, 206, 235))
pause_button_image = load_image('pause.png', (50, 50), (100, 100, 100))  # 暫停按鈕圖像

# 設定按鈕位置
pause_button_rect = pause_button_image.get_rect(topleft=(20, HEIGHT - 70))  # 左下角

# 加載音樂和音效
def load_sound(filename, volume):
    """加載音效"""
    path = 'sound/' + filename
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        return sound
    except pygame.error as e:
        print(f"Error loading sound {filename}: {e}")
        return None

try:
    pygame.mixer.music.load('sound/Gourmet Race(8bit remix).mp3')
    pygame.mixer.music.set_volume(music_volume)
except pygame.error as e:
    print(f"Error loading background music: {e}")

jump_sound = load_sound('monkey-3.wav', sound_volume)
collision_sound = load_sound('qubodup-crash.ogg', sound_volume)

def update_camel():
    """更新駱駝的位置和狀態"""
    global camel_x, camel_y, camel_speed, score, difficulty_level, camel_direction, next_difficulty_score, lives

    camel_x -= camel_speed  # 向左移動 camel

    # 調整速度根據難度
    if difficulty_level == 2 and camel_x < WIDTH / 2:
        camel_speed = random.randint(14, 18)
    elif difficulty_level >= 3:
        camel_speed = 15  # 固定最大速度
    else:
        camel_speed = min(5 + (difficulty_level - 1) * 2, 15)

    if difficulty_level >= 3:
        camel_y += camel_direction * camel_speed_y + random.uniform(-1, 1)
        if camel_y >= camel_vertical_max_y:
            camel_y = camel_vertical_max_y
            camel_direction = -1
        elif camel_y <= camel_vertical_min_y:
            camel_y = camel_vertical_min_y
            camel_direction = 1
    else:
        camel_y = HEIGHT * 0.7

    # 重置 camel 位置並更新分數及難度
    if camel_x < -camel.get_width():
        camel_x = WIDTH
        if difficulty_level >= 3:
            camel_y = random.uniform(camel_vertical_min_y, camel_vertical_max_y)
            camel_direction = random.choice([-1, 1])
        else:
            camel_y = HEIGHT * 0.7

        score += 1
        print(f"分數: {score}")

        # 每5分回覆一生命，在不超過最大生命的情況下
        if score % 5 == 0 and lives < MAX_LIVES:
            lives += 1
            print(f"生命值恢復至 {lives}")

        if score >= next_difficulty_score and difficulty_level < 3:
            difficulty_level += 1
            next_difficulty_score += 10
            print(f"難度等級提升至 {difficulty_level}")

def update_gibbon():
    """更新長臂猿的位置和狀態"""
    global gibbon_y, gibbon_speed, is_jumping, energy
    gibbon_speed += GRAVITY
    gibbon_y += gibbon_speed

    if gibbon_y >= GIBBON_INITIAL_Y:
        gibbon_y = GIBBON_INITIAL_Y
        gibbon_speed = 0
        is_jumping = False
        if energy < 10:
            energy += 10 / ENERGY_CHARGE_TIME

def jump():
    """處理跳躍動作"""
    global gibbon_speed, is_jumping, energy
    if not is_jumping:
        gibbon_speed = JUMP_SPEED - energy * 1.1  # 根據能量調整跳躍高度
        is_jumping = True
        energy = 0
        if jump_sound:
            jump_sound.play()

def check_collision():
    """檢查長臂猿與駱駝的碰撞"""
    gibbon_rect = pygame.Rect(GIBBON_X, gibbon_y, gibbon.get_width(), gibbon.get_height())
    camel_rect = pygame.Rect(camel_x, camel_y, camel.get_width(), camel.get_height())
    return gibbon_rect.colliderect(camel_rect)

def handle_death():
    """處理死亡事件"""
    global lives
    lives -= 1
    print(f"生命值減少至 {lives}")
    if collision_sound:
        collision_sound.play()
    if lives <= 0:
        show_game_over_screen()
    else:
        reset_camel_position()

def reset_camel_position():
    """重置駱駝的位置"""
    global camel_x, camel_y, camel_direction
    camel_x = WIDTH
    if difficulty_level >= 3:
        camel_y = random.uniform(camel_vertical_min_y, camel_vertical_max_y)
        camel_direction = random.choice([-1, 1])
    else:
        camel_y = HEIGHT * 0.7

def show_game_over_screen():
    """顯示遊戲結束畫面"""
    global screen, score
    game_over_font = pygame.font.Font(font_path, 74)
    score_font = pygame.font.Font(font_path, 50)

    game_over_text = game_over_font.render(languages[language]['game_over'], True, (255, 0, 0))
    score_text = score_font.render(languages[language]['final_score'].format(score=score), True, (0, 0, 0))
    restart_text = font.render(languages[language]['restart'], True, (0, 0, 255))
    quit_text = font.render(languages[language]['quit'], True, (255, 0, 0))

    screen.fill((255, 255, 255))
    screen.blit(game_over_text, ((WIDTH - game_over_text.get_width()) // 2, HEIGHT // 2 - 200))
    screen.blit(score_text, ((WIDTH - score_text.get_width()) // 2, HEIGHT // 2 - 100))
    screen.blit(restart_text, ((WIDTH - restart_text.get_width()) // 2, HEIGHT // 2))
    screen.blit(quit_text, ((WIDTH - quit_text.get_width()) // 2, HEIGHT // 2 + 100))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                x, y = event.pos
                if restart_text.get_rect(topleft=((WIDTH - restart_text.get_width()) // 2, HEIGHT // 2)).collidepoint(x, y):
                    waiting = False
                    reset_game()
                    run_game()
                if quit_text.get_rect(topleft=((WIDTH - quit_text.get_width()) // 2, HEIGHT // 2 + 100)).collidepoint(x, y):
                    pygame.quit()
                    sys.exit()
            if event.type == FINGERDOWN:
                touch_x = int(event.x * WIDTH)
                touch_y = int(event.y * HEIGHT)
                if restart_text.get_rect(topleft=((WIDTH - restart_text.get_width()) // 2, HEIGHT // 2)).collidepoint(touch_x, touch_y):
                    waiting = False
                    reset_game()
                    run_game()
                if quit_text.get_rect(topleft=((WIDTH - quit_text.get_width()) // 2, HEIGHT // 2 + 100)).collidepoint(touch_x, touch_y):
                    pygame.quit()
                    sys.exit()

def reset_game():
    """重置遊戲狀態"""
    global score, lives, camel_x, camel_y, camel_speed, difficulty_level, next_difficulty_score
    global gibbon_y, gibbon_speed, is_jumping, energy

    score = 0
    lives = MAX_LIVES
    camel_x = WIDTH
    camel_y = HEIGHT * 0.7
    camel_speed = 5
    difficulty_level = 1
    next_difficulty_score = 10
    gibbon_y = GIBBON_INITIAL_Y
    gibbon_speed = 0
    is_jumping = False
    energy = 0

def update_display():
    """更新遊戲畫面顯示"""
    # 繪製背景和角色
    screen.blit(background, (0, 0))
    screen.blit(gibbon, (GIBBON_X, gibbon_y))
    if camel_x and camel_y:
        screen.blit(camel, (camel_x, camel_y))
    # 繪製暫停按鈕
    screen.blit(pause_button_image, pause_button_rect)

    # 繪製文字資訊
    difficulty_text = font.render(languages[language]['difficulty_level'].format(difficulty=difficulty_level), True, (0, 0, 0))
    score_text = font.render(languages[language]['score'].format(score=score), True, (0, 0, 0))
    energy_display = min(int(energy), 5)
    energy_text = font.render(languages[language]['energy'].format(energy='█' * energy_display), True, (0, 0, 0))
    lives_text = font.render(languages[language]['lives'].format(lives='●' * lives), True, (255, 0, 0))

    screen.blit(difficulty_text, (10, 10))
    screen.blit(score_text, (250, 10))
    screen.blit(energy_text, (490, 10))
    screen.blit(lives_text, (800, 10))

    if paused:
        paused_text = font.render(languages[language]['paused'], True, (255, 0, 0))
        screen.blit(paused_text, ((WIDTH - paused_text.get_width()) // 2, HEIGHT // 2))

    pygame.display.update()

def run_game():
    """運行遊戲主迴圈"""
    global is_jumping, paused, music_volume, sound_volume
    pygame.mixer.music.play(-1)
    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = event.pos
                    if pause_button_rect.collidepoint(mouse_pos):
                        print("開啟設定")
                        settings_menu()  # 改為開啟設定菜單
                    elif not paused:
                        jump()
            elif event.type == FINGERDOWN:
                touch_x = int(event.x * WIDTH)
                touch_y = int(event.y * HEIGHT)
                if pygame.Rect(pause_button_rect).collidepoint(touch_x, touch_y):
                    print("開啟設定")
                    settings_menu()  # 改為開啟設定菜單
                elif not paused:
                    jump()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE and not paused:
                    jump()

        if not paused:
            update_gibbon()
            update_camel()

            if check_collision():
                handle_death()

        update_display()

def main_menu():
    """顯示主選單並等待用戶操作"""
    pygame.mixer.music.stop()
    while True:
        screen.fill((255, 255, 255))
        title_text = font.render(languages[language]['main_menu_title'], True, (0, 0, 0))
        start_text = font.render(languages[language]['play'], True, (0, 0, 0))
        
        if language == 'zh-TW':
            toggle_language_label = languages['en']['english']
            target_lang = 'en'
        else:
            toggle_language_label = languages['zh-TW']['chinese']
            target_lang = 'zh-TW'
        language_text = font.render(toggle_language_label, True, (0, 0, 0))
        
        credits_text = font.render(languages[language]['credits'], True, (0, 0, 0))

        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 200))
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 300))
        screen.blit(language_text, (WIDTH // 2 - language_text.get_width() // 2, 400))
        screen.blit(credits_text, (WIDTH // 2 - credits_text.get_width() // 2, 500))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type in (MOUSEBUTTONDOWN, FINGERDOWN):
                if event.type == MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                else:
                    mouse_pos = (int(event.x * WIDTH), int(event.y * HEIGHT))
                if start_text.get_rect(topleft=(WIDTH // 2 - start_text.get_width() // 2, 300)).collidepoint(mouse_pos):
                    run_game()
                elif language_text.get_rect(topleft=(WIDTH // 2 - language_text.get_width() // 2, 400)).collidepoint(mouse_pos):
                    set_language(target_lang)
                elif credits_text.get_rect(topleft=(WIDTH // 2 - credits_text.get_width() // 2, 500)).collidepoint(mouse_pos):
                    copyright_menu()

def settings_menu():
    """顯示設定選單"""
    global music_volume, sound_volume, jump_sound, collision_sound
    dragging_music = False
    dragging_sound = False

    slider_width = 300
    slider_height = 20
    handle_radius = 10

    music_handle_x = WIDTH // 2 - slider_width // 2 + int(music_volume * slider_width)
    sound_handle_x = WIDTH // 2 - slider_width // 2 + int(sound_volume * slider_width)

    clock = pygame.time.Clock()

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    if WIDTH // 2 - slider_width // 2 <= mouse_x <= WIDTH // 2 + slider_width // 2 and 180 <= mouse_y <= 200:
                        dragging_music = True
                    elif WIDTH // 2 - slider_width // 2 <= mouse_x <= WIDTH // 2 + slider_width // 2 and 280 <= mouse_y <= 300:
                        dragging_sound = True
                    elif back_text.get_rect(topleft=(WIDTH // 2 - back_text.get_width() // 2, 460)).collidepoint(event.pos):
                        return
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    dragging_music = False
                    dragging_sound = False
            elif event.type == MOUSEMOTION:
                if dragging_music:
                    mouse_x, _ = event.pos
                    music_handle_x = max(WIDTH // 2 - slider_width // 2, min(mouse_x, WIDTH // 2 + slider_width // 2))
                    music_volume = (music_handle_x - (WIDTH // 2 - slider_width // 2)) / slider_width
                    music_volume = max(0.0, min(music_volume, 1.0))
                    pygame.mixer.music.set_volume(music_volume)
                if dragging_sound:
                    mouse_x, _ = event.pos
                    sound_handle_x = max(WIDTH // 2 - slider_width // 2, min(mouse_x, WIDTH // 2 + slider_width // 2))
                    sound_volume = (sound_handle_x - (WIDTH // 2 - slider_width // 2)) / slider_width
                    sound_volume = max(0.0, min(sound_volume, 1.0))
                    if jump_sound:
                        jump_sound.set_volume(sound_volume)
                    if collision_sound:
                        collision_sound.set_volume(sound_volume)
            elif event.type == FINGERDOWN:
                touch_x = int(event.x * WIDTH)
                touch_y = int(event.y * HEIGHT)
                if back_text.get_rect(topleft=(WIDTH // 2 - back_text.get_width() // 2, 460)).collidepoint((touch_x, touch_y)):
                    return
            elif event.type == FINGERMOTION:
                if dragging_music:
                    touch_x = int(event.x * WIDTH)
                    music_handle_x = max(WIDTH // 2 - slider_width // 2, min(touch_x, WIDTH // 2 + slider_width // 2))
                    music_volume = (music_handle_x - (WIDTH // 2 - slider_width // 2)) / slider_width
                    music_volume = max(0.0, min(music_volume, 1.0))
                    pygame.mixer.music.set_volume(music_volume)
                if dragging_sound:
                    touch_x = int(event.x * WIDTH)
                    sound_handle_x = max(WIDTH // 2 - slider_width // 2, min(touch_x, WIDTH // 2 + slider_width // 2))
                    sound_volume = (sound_handle_x - (WIDTH // 2 - slider_width // 2)) / slider_width
                    sound_volume = max(0.0, min(sound_volume, 1.0))
                    if jump_sound:
                        jump_sound.set_volume(sound_volume)
                    if collision_sound:
                        collision_sound.set_volume(sound_volume)

        # 更新畫面
        screen.fill((220, 220, 220))  # 更淺的背景色
        settings_title = font.render("設定", True, (0, 0, 0))  # 設定標題
        back_text = font.render(languages[language]['back'], True, (0, 0, 255))
        music_label = font.render(languages[language]['volume_music'], True, (0, 0, 0))
        sound_label = font.render(languages[language]['volume_sound'], True, (0, 0, 0))

        # 繪製設定標題
        screen.blit(settings_title, (WIDTH // 2 - settings_title.get_width() // 2, 30))

        # 繪製音樂音量滑桿
        screen.blit(music_label, (WIDTH // 2 - music_label.get_width() // 2, 150))
        pygame.draw.rect(screen, (169, 169, 169), (WIDTH // 2 - slider_width // 2, 150 + music_label.get_height() + 10, slider_width, slider_height))
        pygame.draw.circle(screen, (50, 50, 50), (music_handle_x, 150 + music_label.get_height() + 10 + slider_height // 2), handle_radius)

        # 繪製音效音量滑桿
        screen.blit(sound_label, (WIDTH // 2 - sound_label.get_width() // 2, 250))
        pygame.draw.rect(screen, (169, 169, 169), (WIDTH // 2 - slider_width // 2, 250 + sound_label.get_height() + 10, slider_width, slider_height))
        pygame.draw.circle(screen, (50, 50, 50), (sound_handle_x, 250 + sound_label.get_height() + 10 + slider_height // 2), handle_radius)

        # 繪製返回按鈕
        screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, 350))

        pygame.display.update()

def pause_menu():
    """顯示暫停選單"""
    global paused
    while paused:
        screen.fill((0, 0, 0))
        paused_text = font.render(languages[language]['paused'], True, (255, 255, 255))
        screen.blit(paused_text, ((WIDTH - paused_text.get_width()) // 2, HEIGHT // 2))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    paused = False
            elif event.type == FINGERDOWN:
                paused = False

def copyright_menu():
    """顯示版權資訊"""
    while True:
        screen.fill((255, 255, 255))
        credits_title = font.render(languages[language]['credits'], True, (0, 0, 0))
        credits_lines = languages[language]['credits_text'].split('\n')
        reversed_credits = credits_lines[::-1]  # 上下顛倒
        for i, line in enumerate(reversed_credits):
            credits_text_render = font.render(line, True, (0, 0, 0))
            screen.blit(credits_text_render, (WIDTH // 2 - credits_text_render.get_width() // 2, 200 + i * 40))
        back_text = font.render(languages[language]['back'], True, (0, 0, 255))
        screen.blit(credits_title, (WIDTH // 2 - credits_title.get_width() // 2, 100))
        screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, 600))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type in (MOUSEBUTTONDOWN, FINGERDOWN):
                if event.type == MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                else:
                    mouse_pos = (int(event.x * WIDTH), int(event.y * HEIGHT))
                if back_text.get_rect(topleft=(WIDTH // 2 - back_text.get_width() // 2, 600)).collidepoint(mouse_pos):
                    return
            if event.type == KEYDOWN:
                if event.key == K_b:
                    return

if __name__ == "__main__":
    main_menu()