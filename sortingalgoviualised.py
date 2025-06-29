import pygame
import sys
import random
import colorsys
import math
import numpy as np

# Setup
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 600, 700  # Increased height to fit bar chart
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rainbow Pie Chart + Bar Chart Sort Visualizer")
CENTER = (WIDTH // 2, HEIGHT // 2 - 50)
RADIUS = 250
NUM_COLORS = 100
FPS = 120

# Generate HSV colors
original_hsv = [(i / NUM_COLORS, 1, 1) for i in range(NUM_COLORS)]
colors_hsv = random.sample(original_hsv, len(original_hsv))

# Sound setup
sound_cache = {}

def hue_to_frequency(hue):
    return 220 + hue * (880 - 220)

def create_beep_sound(frequency, duration_ms=100, volume=0.3):
    sample_rate = 44100
    n_samples = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, duration_ms / 1000, n_samples, False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    # Apply fade in/out envelope (10 ms fade)
    fade_len = int(sample_rate * 0.01)  # 10 ms fade in/out
    envelope = np.ones(n_samples)
    envelope[:fade_len] = np.linspace(0, 1, fade_len)       # fade in
    envelope[-fade_len:] = np.linspace(1, 0, fade_len)      # fade out
    
    wave *= envelope

    audio = np.int16(wave * 32767)
    stereo_audio = np.column_stack((audio, audio))
    sound = pygame.sndarray.make_sound(stereo_audio)
    sound.set_volume(volume)
    return sound

def get_tone_for_hue(hue):
    freq = round(hue_to_frequency(hue))
    if freq not in sound_cache:
        sound_cache[freq] = create_beep_sound(freq)
    return sound_cache[freq]

# Utility functions
def hsv_to_rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))

def draw_pie_segment(surface, color, center, radius, start_angle, end_angle, width=0):
    points = [center]
    for angle in range(int(start_angle), int(end_angle) + 1):
        rad = math.radians(angle)
        x = center[0] + radius * math.cos(rad)
        y = center[1] + radius * math.sin(rad)
        points.append((x, y))
    pygame.draw.polygon(surface, color, points, width)

def draw_bar_chart(colors_rgb, highlight_indices=[]):
    chart_top = HEIGHT - 90
    bar_width = WIDTH / len(colors_rgb)
    max_height = 80

    for i, color in enumerate(colors_rgb):
        # Convert RGB back to HSV to get the hue
        r, g, b = color
        h, _, _ = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)

        # Map hue inversely: red (h=0) → tallest, violet (h≈1) → shortest
        hue_height = (1.0 - h) * max_height
        x = i * bar_width
        y = chart_top + (max_height - hue_height)

        pygame.draw.rect(screen, color, (x, y, bar_width, hue_height))
        if i in highlight_indices:
            pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, hue_height), 2)

# Sorting Algorithms
def bubble_sort(colors):
    n = len(colors)
    for i in range(n):
        for j in range(n - i - 1):
            yield colors, [j, j + 1]
            if colors[j][0] > colors[j + 1][0]:
                colors[j], colors[j + 1] = colors[j + 1], colors[j]
                get_tone_for_hue(colors[j][0]).play()

def insertion_sort(colors):
    for i in range(1, len(colors)):
        key = colors[i]
        j = i - 1
        while j >= 0 and colors[j][0] > key[0]:
            yield colors, [j, j + 1]
            colors[j + 1] = colors[j]
            j -= 1
            get_tone_for_hue(colors[j + 1][0]).play()
        colors[j + 1] = key
        yield colors, [j + 1]

def selection_sort(colors):
    n = len(colors)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            yield colors, [min_idx, j]
            if colors[j][0] < colors[min_idx][0]:
                min_idx = j
        colors[i], colors[min_idx] = colors[min_idx], colors[i]
        get_tone_for_hue(colors[i][0]).play()
        yield colors, [i, min_idx]

def merge_sort(colors, start=0, end=None):
    if end is None:
        end = len(colors)
    if end - start > 1:
        mid = (start + end) // 2
        yield from merge_sort(colors, start, mid)
        yield from merge_sort(colors, mid, end)
        merged = []
        i, j = start, mid
        while i < mid and j < end:
            yield colors, [i, j]
            if colors[i][0] < colors[j][0]:
                merged.append(colors[i])
                i += 1
            else:
                merged.append(colors[j])
                j += 1
            get_tone_for_hue(merged[-1][0]).play()
        while i < mid:
            merged.append(colors[i])
            i += 1
        while j < end:
            merged.append(colors[j])
            j += 1
        for i, val in enumerate(merged):
            colors[start + i] = val
            yield colors, [start + i]

def stalin_sort(colors):
    if not colors:
        return
    i = 0
    for j in range(1, len(colors)):
        yield colors, [i, j]
        if colors[j][0] >= colors[i][0]:
            i += 1
            colors[i] = colors[j]
            get_tone_for_hue(colors[i][0]).play()
            yield colors, [i]
    for k in range(i + 1, len(colors)):
        colors[k] = (0, 0, 0)
        yield colors, [k]

def bogo_sort(colors):
    def is_sorted(arr):
        return all(arr[i][0] <= arr[i+1][0] for i in range(len(arr)-1))
    while not is_sorted(colors):
        random.shuffle(colors)
        for c in colors:
            get_tone_for_hue(c[0]).play()
        yield colors, list(range(len(colors)))
    yield colors, []

# Drawing functions
def draw_info_bar(sort_type, num_elements, sorting):
    font = pygame.font.SysFont(None, 28)
    info_height = 35
    info_rect = pygame.Rect(0, 0, WIDTH, info_height)
    pygame.draw.rect(screen, (50, 50, 50), info_rect)
    status_text = "Sorting..." if sorting else "Idle"
    text = f"Sort: {sort_type.title()} | Elements: {num_elements} | Status: {status_text}"
    rendered_text = font.render(text, True, (255, 255, 255))
    screen.blit(rendered_text, (10, 7))

def draw_pie_chart(colors_rgb, highlight_indices=[], sort_type="Bubble", sorting=False):
    screen.fill((30, 30, 30))
    draw_info_bar(sort_type, len(colors_rgb), sorting)
    angle_per_segment = 360 / len(colors_rgb)
    for i, color in enumerate(colors_rgb):
        start_angle = i * angle_per_segment - 90
        end_angle = start_angle + angle_per_segment
        draw_pie_segment(screen, color, CENTER, RADIUS, start_angle, end_angle)
        if i in highlight_indices:
            draw_pie_segment(screen, (255, 255, 255), CENTER, RADIUS, start_angle, end_angle, width=2)
    draw_bar_chart(colors_rgb, highlight_indices)
    pygame.display.update()

# Reset state
def reset_state():
    global colors_hsv
    colors_hsv = random.sample(original_hsv, len(original_hsv))
    return None, False

# Main loop
def main():
    global colors_hsv
    clock = pygame.time.Clock()
    sorting = False
    sorter = None
    selected_sort = "bubble"
    draw_pie_chart([hsv_to_rgb(*c) for c in colors_hsv], sort_type=selected_sort, sorting=sorting)

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not sorting:
                    sorting = True
                    if selected_sort == "bubble":
                        sorter = bubble_sort(colors_hsv)
                    elif selected_sort == "insertion":
                        sorter = insertion_sort(colors_hsv)
                    elif selected_sort == "selection":
                        sorter = selection_sort(colors_hsv)
                    elif selected_sort == "merge":
                        sorter = merge_sort(colors_hsv)
                    elif selected_sort == "stalin":
                        sorter = stalin_sort(colors_hsv)
                    elif selected_sort == "bogo":
                        sorter = bogo_sort(colors_hsv)
                elif event.key == pygame.K_r:
                    sorter, sorting = reset_state()
                elif event.key == pygame.K_b:
                    selected_sort = "bubble"
                    sorter, sorting = reset_state()
                elif event.key == pygame.K_i:
                    selected_sort = "insertion"
                    sorter, sorting = reset_state()
                elif event.key == pygame.K_s:
                    selected_sort = "selection"
                    sorter, sorting = reset_state()
                elif event.key == pygame.K_m:
                    selected_sort = "merge"
                    sorter, sorting = reset_state()
                elif event.key == pygame.K_t:
                    selected_sort = "stalin"
                    sorter, sorting = reset_state()
                elif event.key == pygame.K_g:
                    selected_sort = "bogo"
                    sorter, sorting = reset_state()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        if sorting and sorter:
            try:
                current, highlights = next(sorter)
                draw_pie_chart([hsv_to_rgb(*c) for c in current], highlight_indices=highlights, sort_type=selected_sort, sorting=True)
            except StopIteration:
                sorter = None
                sorting = False
                draw_pie_chart([hsv_to_rgb(*c) for c in colors_hsv], sort_type=selected_sort, sorting=False)
        else:
            draw_pie_chart([hsv_to_rgb(*c) for c in colors_hsv], sort_type=selected_sort, sorting=False)

if __name__ == "__main__":
    main()
