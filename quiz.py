import tkinter as tk
from tkinter import ttk, messagebox
import paho.mqtt.client as mqtt

class BuzzerQuiz:
    def __init__(self, master):
        self.master = master
        self.master.title("Buzzer Quiz")
        self.master.geometry("800x600")

        self.players = ["Spieler 1", "Spieler 2", "Spieler 3", "Spieler 4"]
        self.scores = [0, 0, 0, 0]
        self.buzzer_order = []
        self.is_quiz_active = False

        self.create_widgets()
        self.setup_mqtt()

    def create_widgets(self):
        # Scoreboard
        self.scoreboard_frame = ttk.Frame(self.master, padding="10")
        self.scoreboard_frame.pack(fill=tk.X)

        self.name_entries = []
        self.score_entries = []
        for i in range(4):
            name_entry = ttk.Entry(self.scoreboard_frame, width=15)
            name_entry.insert(0, self.players[i])
            name_entry.grid(row=0, column=i*2, padx=5, pady=5)
            self.name_entries.append(name_entry)

            score_entry = ttk.Entry(self.scoreboard_frame, width=5)
            score_entry.insert(0, "0")
            score_entry.grid(row=0, column=i*2+1, padx=5, pady=5)
            self.score_entries.append(score_entry)

        # Control buttons
        self.control_frame = ttk.Frame(self.master, padding="10")
        self.control_frame.pack(fill=tk.X)

        self.test_button = ttk.Button(self.control_frame, text="Test", command=self.test_mode)
        self.test_button.pack(side=tk.LEFT, padx=5)

        self.start_quiz_button = ttk.Button(self.control_frame, text="Quiz starten", command=self.start_quiz)
        self.start_quiz_button.pack(side=tk.LEFT, padx=5)

        # Quiz frame (initially hidden)
        self.quiz_frame = ttk.Frame(self.master, padding="10")

        self.order_listbox = tk.Listbox(self.quiz_frame, height=10, width=40)
        self.order_listbox.pack(fill=tk.BOTH, expand=True)

        self.next_round_button = ttk.Button(self.quiz_frame, text="Nächste Runde", command=self.next_round)
        self.next_round_button.pack(side=tk.LEFT, padx=5)

        self.end_quiz_button = ttk.Button(self.quiz_frame, text="Quiz beenden", command=self.end_quiz)
        self.end_quiz_button.pack(side=tk.LEFT, padx=5)

    def test_mode(self):
        self.is_quiz_active = False
        self.order_listbox.delete(0, tk.END)
        self.quiz_frame.pack(fill=tk.BOTH, expand=True)
        self.order_listbox.insert(tk.END, "Testmodus: Drücken Sie die Buzzer")

    def start_quiz(self):
        self.is_quiz_active = True
        self.control_frame.pack_forget()
        self.quiz_frame.pack(fill=tk.BOTH, expand=True)
        self.next_round()

    def next_round(self):
        self.buzzer_order = []
        self.order_listbox.delete(0, tk.END)
        self.order_listbox.insert(tk.END, "Neue Runde: Drücken Sie die Buzzer")

    def end_quiz(self):
        self.is_quiz_active = False
        self.quiz_frame.pack_forget()
        self.control_frame.pack(fill=tk.X)
        self.update_scores()
        self.show_final_ranking()

    def update_scores(self):
        for i, entry in enumerate(self.score_entries):
            self.scores[i] = int(entry.get())

    def show_final_ranking(self):
        ranking = sorted(zip(self.players, self.scores), key=lambda x: x[1], reverse=True)
        result = "Finale Rangliste:\n"
        for player, score in ranking:
            result += f"{player}: {score} Punkte\n"
        messagebox.showinfo("Quizergebnis", result)

    def setup_mqtt(self):
        self.client = mqtt.Client(client_id="laptop", protocol=mqtt.MQTTv311)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("192.168.178.83", 1883, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe("buzzer/pressed")

    def on_message(self, client, userdata, msg):
        if msg.topic == "buzzer/pressed":
            player_index = int(msg.payload.decode()) - 1
            self.master.after(0, self.buzzer_pressed, player_index)

    def buzzer_pressed(self, player_index):
        if self.is_quiz_active and player_index not in self.buzzer_order:
            self.buzzer_order.append(player_index)
            self.order_listbox.insert(tk.END, f"Spieler {player_index + 1}")
        elif not self.is_quiz_active:
            self.order_listbox.insert(tk.END, f"Testmodus: Spieler {player_index + 1} hat gedrückt")


if __name__ == "__main__":
    root = tk.Tk()
    app = BuzzerQuiz(root)
    root.mainloop()
