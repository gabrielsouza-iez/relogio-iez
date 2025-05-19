import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import datetime
import threading
import time

HORARIO_SAIDA = "17:00"
LARGURA_JANELA = 400
ALTURA_JANELA = 150
VELOCIDADE = 5
IMAGEM_CAMINHO = "bannerIEZ.png"

class DVDApp:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)  # Remove bordas
        self.root.attributes("-topmost", True)
        self.root.configure(bg="black")

        self.canvas = tk.Canvas(root, width=LARGURA_JANELA, height=ALTURA_JANELA, highlightthickness=0)
        self.canvas.pack()

        # Carregar imagem de fundo
        try:
            img = Image.open(IMAGEM_CAMINHO).resize((LARGURA_JANELA, ALTURA_JANELA))
            self.bg_image = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_image)
        except Exception as e:
            print("Erro ao carregar imagem:", e)

        # Fundo escuro atrás do texto (como uma faixa retangular)
        self.text_bg = self.canvas.create_rectangle(
            20, 20, LARGURA_JANELA - 20, ALTURA_JANELA - 20,
            fill="#000000", outline="", stipple="gray50"
        )

        # Texto informativo
        self.label_info = self.canvas.create_text(
            LARGURA_JANELA//2, 40,
            text="Tempo restante para ir embora:",
            fill="white",
            font=("Arial", 10, "bold")
        )

        # Contador de tempo
        self.label_timer = self.canvas.create_text(
            LARGURA_JANELA//2, 90,
            text="Calculando...",
            fill="white",
            font=("Arial", 16, "bold")
        )

        self.pos_x = 100
        self.pos_y = 100
        self.vel_x = VELOCIDADE
        self.vel_y = VELOCIDADE
        self.alert_shown = False
        self.bouncing_enabled = False

        threading.Thread(target=self.atualizar_tempo, daemon=True).start()
        self.mover_janela()

    def atualizar_tempo(self):
        try:
            saida = datetime.datetime.strptime(HORARIO_SAIDA, "%H:%M").time()
        except ValueError:
            self.canvas.itemconfig(self.label_timer, text="Erro no horário")
            return

        while True:
            agora = datetime.datetime.now()
            saida_hoje = datetime.datetime.combine(agora.date(), saida)
            if agora > saida_hoje:
                saida_hoje += datetime.timedelta(days=1)

            restante = saida_hoje - agora

            if restante.total_seconds() <= 0:
                self.canvas.itemconfig(self.label_timer, text="✨ HORA DE IR EMBORA! ✨")
                self.alert_shown = False
                self.bouncing_enabled = False
            else:
                if restante <= datetime.timedelta(minutes=10):
                    if not self.alert_shown:
                        self.root.after(0, lambda: messagebox.showinfo("Atenção", "Faltam menos de 10 minutos para ir embora!"))
                        self.alert_shown = True
                    self.bouncing_enabled = True

                horas, resto = divmod(int(restante.total_seconds()), 3600)
                minutos, segundos = divmod(resto, 60)
                texto = f"{horas:02}:{minutos:02}:{segundos:02}"
                self.canvas.itemconfig(self.label_timer, text=texto)

            time.sleep(1)

    def mover_janela(self):
        if self.bouncing_enabled:
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()

            if self.pos_x + LARGURA_JANELA >= screen_w or self.pos_x <= 0:
                self.vel_x = -self.vel_x
            if self.pos_y + ALTURA_JANELA >= screen_h or self.pos_y <= 0:
                self.vel_y = -self.vel_y

            self.pos_x += self.vel_x
            self.pos_y += self.vel_y

            self.root.geometry(f"{LARGURA_JANELA}x{ALTURA_JANELA}+{self.pos_x}+{self.pos_y}")

        self.root.after(30, self.mover_janela)

def main():
    root = tk.Tk()
    app = DVDApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
