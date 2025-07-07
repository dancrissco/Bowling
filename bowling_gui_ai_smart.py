import tkinter as tk
import threading
import pybullet as p
import pybullet_data
import numpy as np
import time
import random
import platform

# Sound playback
def play_hit_sound():
    try:
        if platform.system() == "Windows":
            import winsound
            winsound.PlaySound("hit.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            from playsound import playsound
            playsound("hit.wav", block=False)
    except Exception as e:
        print("Sound error:", e)

class BowlingGame:
    def __init__(self, root):
        self.root = root
        self.frame = 1
        self.max_frames = 5
        self.player_score = 0
        self.ai_score = 0

        # GUI Setup
        root.title("Bowling Simulator with AI Opponent")

        self.score_label = tk.Label(root, text="Frame 1 / 5", font=("Arial", 16))
        self.score_label.pack(pady=5)

        self.player_score_label = tk.Label(root, text="Player Score: 0", font=("Arial", 14))
        self.player_score_label.pack()

        self.ai_score_label = tk.Label(root, text="AI Score: 0", font=("Arial", 14))
        self.ai_score_label.pack()

        tk.Label(root, text="Your Ball X Position").pack()
        self.x_slider = tk.Scale(root, from_=-0.3, to=0.3, resolution=0.01, orient=tk.HORIZONTAL, length=300)
        self.x_slider.set(0.0)
        self.x_slider.pack()

        tk.Label(root, text="Your Ball Angle (degrees)").pack()
        self.angle_slider = tk.Scale(root, from_=-30, to=30, resolution=1, orient=tk.HORIZONTAL, length=300)
        self.angle_slider.set(0)
        self.angle_slider.pack()

        self.throw_button = tk.Button(root, text="Throw Ball", command=self.start_throw, font=("Arial", 14))
        self.throw_button.pack(pady=10)

        self.status_label = tk.Label(root, text="Click 'Throw Ball' to start your turn.", font=("Arial", 12))
        self.status_label.pack()

        threading.Thread(target=self.setup_simulation, daemon=True).start()

    def setup_simulation(self):
        self.client = p.connect(p.GUI)
        p.setGravity(0, 0, -9.8)
        p.setTimeStep(1. / 240.)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.loadURDF("plane.urdf")

        # Wooden lane
        lane_col = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.5, 2.5, 0.01])
        lane_vis = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.5, 2.5, 0.01], rgbaColor=[0.6, 0.4, 0.2, 1])
        p.createMultiBody(baseMass=0, baseCollisionShapeIndex=lane_col, baseVisualShapeIndex=lane_vis,
                          basePosition=[0, 1.25, 0])

        self.wait_for_throw()

    def wait_for_throw(self):
        while self.frame <= self.max_frames:
            time.sleep(0.01)
            p.stepSimulation()

    def start_throw(self):
        if self.frame > self.max_frames:
            self.status_label.config(text="Game Over.")
            return

        self.throw_button.config(state=tk.DISABLED)
        threading.Thread(target=self.run_player_and_ai_round, daemon=True).start()

    def run_player_and_ai_round(self):
        # --- Player's Turn ---
        self.status_label.config(text=f"Frame {self.frame}: Player's Turn...")
        knocked = self.run_single_throw(self.x_slider.get(), self.angle_slider.get())
        self.player_score += knocked
        self.player_score_label.config(text=f"Player Score: {self.player_score}")
        self.status_label.config(text=f"You knocked {knocked} pins!")

        time.sleep(1)

        # --- AI's Turn ---
        self.status_label.config(text=f"Frame {self.frame}: AI's Turn...")
        #ai_x = random.uniform(-0.2, 0.2)
        #ai_angle = random.uniform(-15, 15)
        # 🎯 Targeted AI throws toward 1-3 pocket
        base_x = 0.05         # ideal X for strike
        base_angle = -3       # slight curve into 1-3 pocket
        ai_x = random.uniform(base_x - 0.03, base_x + 0.03)
        ai_angle = random.uniform(base_angle - 3, base_angle + 3)
        
        knocked = self.run_single_throw(ai_x, ai_angle)
        self.ai_score += knocked
        self.ai_score_label.config(text=f"AI Score: {self.ai_score}")
        self.status_label.config(text=f"AI knocked {knocked} pins!")

        self.frame += 1
        self.score_label.config(text=f"Frame {self.frame} / {self.max_frames}" if self.frame <= self.max_frames else "Game Over")

        if self.frame <= self.max_frames:
            self.throw_button.config(state=tk.NORMAL)
        else:
            winner = "Player" if self.player_score > self.ai_score else "AI" if self.ai_score > self.player_score else "It's a tie"
            self.status_label.config(text=f"Game Over! Final Scores - Player: {self.player_score}, AI: {self.ai_score}. {winner} wins!")

    def run_single_throw(self, x_offset, angle_deg):
        # Cleanup
        if hasattr(self, 'ball_id'):
            p.removeBody(self.ball_id)
        if hasattr(self, 'pin_ids'):
            for pid in self.pin_ids:
                p.removeBody(pid)

        # Spawn pins
        self.pin_ids = []
        for i in range(5):
            pin_col = p.createCollisionShape(p.GEOM_CYLINDER, radius=0.03, height=0.2)
            pin_vis = p.createVisualShape(p.GEOM_CYLINDER, radius=0.03, length=0.2, rgbaColor=[0.9, 0.9, 0.2, 1])
            pin_id = p.createMultiBody(baseMass=0.1,
                                       baseCollisionShapeIndex=pin_col,
                                       baseVisualShapeIndex=pin_vis,
                                       basePosition=[(i - 2) * 0.1, 2.2, 0.1])
            self.pin_ids.append(pin_id)

        # Spawn ball
        self.ball_id = self.spawn_ball(x_offset, angle_deg)

        for _ in range(300):
            p.stepSimulation()
            time.sleep(1 / 240.)

        knocked = self.pins_knocked()
        if knocked > 0:
            play_hit_sound()

        self.camera_fly_in()
        return knocked

    def spawn_ball(self, x_offset, angle_deg):
        ball_col = p.createCollisionShape(p.GEOM_SPHERE, radius=0.05)
        ball_vis = p.createVisualShape(p.GEOM_SPHERE, radius=0.05, rgbaColor=[0.2, 0.2, 0.8, 1])
        ball_id = p.createMultiBody(baseMass=1,
                                    baseCollisionShapeIndex=ball_col,
                                    baseVisualShapeIndex=ball_vis,
                                    basePosition=[x_offset, 0, 0.05])

        angle_rad = np.deg2rad(angle_deg)
        vx = np.sin(angle_rad) * 4
        vy = np.cos(angle_rad) * 4
        p.resetBaseVelocity(ball_id, linearVelocity=[vx, vy, 0])
        return ball_id

    def pins_knocked(self):
        count = 0
        for pid in self.pin_ids:
            pos, orn = p.getBasePositionAndOrientation(pid)
            rot = p.getMatrixFromQuaternion(orn)
            up_z = rot[8]
            if abs(up_z) < 0.7:
                count += 1
        return count

    def camera_fly_in(self):
        target = [0, 2.2, 0.1]
        for step in range(60):
            yaw = 180 + step * 2
            pitch = -30 + (step * 0.5)
            distance = 1.5 - step * 0.01
            p.resetDebugVisualizerCamera(distance, yaw, pitch, target)
            time.sleep(1 / 60)

if __name__ == "__main__":
    root = tk.Tk()
    game = BowlingGame(root)
    root.mainloop()
