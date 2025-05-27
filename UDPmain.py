import subprocess
import os
import time
import pygame

def play_music():
    pygame.mixer.init()
    music_path = os.path.join(os.path.dirname(__file__), "assets", "bg_music.wav")
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(0.5)  # Volume 0.0 - 1.0
    pygame.mixer.music.play(-1)  # -1 artinya repeat terus

def run_scripts():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    controller_path = os.path.join(base_dir, "UDPcontroller.py")
    game_path = os.path.join(base_dir, "UDPSnakeGame2Player.py")

    play_music()

    controller_proc = subprocess.Popen(["python", controller_path])
    time.sleep(3)  # Delay agar kamera dan controller siap
    game_proc = subprocess.Popen(["python", game_path])

    print("🎵 Musik dimulai • 🎮 Game & kontroler UDP dijalankan")

    try:
        controller_proc.wait()
        game_proc.wait()
    except KeyboardInterrupt:
        print("\n❌ Dihentikan oleh user.")
        controller_proc.terminate()
        game_proc.terminate()
        pygame.mixer.music.stop()

if __name__ == "__main__":
    run_scripts()