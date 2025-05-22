import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import datetime
import threading
import time
import pygame
import os

LARGURA_JANELA = 400
ALTURA_JANELA = 150
VELOCIDADE = 7
IMAGEM_CAMINHO = "bannerIEZ.png"
SOM_PATH = "som-do-zap-zap-estourado.mp3"

class DVDApp:
    def __init__(self, root, horario_saida, voltar_callback):
        self.root = root
        self.horario_saida = horario_saida
        self.voltar_callback = voltar_callback
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        self.pos_x = 100
        self.pos_y = 100
        self.vel_x = VELOCIDADE
        self.vel_y = VELOCIDADE
        self.alert_shown = False
        self.bouncing_enabled = False
        self.som_ativo = True

        self.root.geometry(f"{LARGURA_JANELA}x{ALTURA_JANELA}+{self.pos_x}+{self.pos_y}")

        try:
            img = Image.open(IMAGEM_CAMINHO).resize((LARGURA_JANELA, ALTURA_JANELA))
            self.bg_image = ImageTk.PhotoImage(img)
            self.label_image = tk.Label(root, image=self.bg_image)
            self.label_image.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print("Erro ao carregar imagem:", e)

        self.label_info = tk.Label(
            root,
            text="Tempo restante para ir embora:",
            fg="white",
            bg="#ff6600",
            font=("Arial", 10, "bold")
        )
        self.label_info.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

        self.label_timer = tk.Label(
            root, text="Calculando...",
            fg="white", bg="black", font=("Arial", 16, "bold")
        )
        self.label_timer.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        self.btn_voltar = tk.Button(root, text="Voltar", command=self.voltar)
        self.btn_voltar.place(relx=0.25, rely=0.75, anchor=tk.CENTER)

        self.btn_toggle_bounce = tk.Button(root, text="Parar Bouncing", command=self.toggle_bouncing)
        self.btn_toggle_bounce.place(relx=0.75, rely=0.75, anchor=tk.CENTER)

        self.btn_toggle_sound = tk.Button(root, text="Desativar Som", command=self.toggle_sound)
        self.btn_toggle_sound.place(relx=0.5, rely=0.85, anchor=tk.CENTER)

        # Atalho para parar movimentação: barra de espaço
        self.root.bind('<space>', lambda e: self.toggle_bouncing())

        self.brilho_valor = 0
        self.brilho_direcao = 1
        self.animar_brilho()

        # Inicializa som
        pygame.mixer.init()
        if os.path.exists(SOM_PATH):
            self.som = pygame.mixer.Sound(SOM_PATH)
        else:
            self.som = None
            print("Arquivo de som não encontrado.")

        threading.Thread(target=self.atualizar_tempo, daemon=True).start()
        self.mover_janela()

    def voltar(self):
        self.root.withdraw()
        self.voltar_callback()

    def toggle_bouncing(self):
        self.bouncing_enabled = not self.bouncing_enabled
        if self.bouncing_enabled:
            self.btn_toggle_bounce.config(text="Parar Bouncing")
        else:
            self.btn_toggle_bounce.config(text="Iniciar Bouncing")

    def toggle_sound(self):
        self.som_ativo = not self.som_ativo
        if self.som_ativo:
            self.btn_toggle_sound.config(text="Desativar Som")
        else:
            self.btn_toggle_sound.config(text="Ativar Som")

    def atualizar_tempo(self):
        saida = datetime.datetime.strptime(self.horario_saida, "%H:%M").time()
        while True:
            agora = datetime.datetime.now()
            saida_hoje = datetime.datetime.combine(agora.date(), saida)
            if agora > saida_hoje:
                saida_hoje += datetime.timedelta(days=1)

            restante = saida_hoje - agora
            if restante.total_seconds() <= 0:
                self.label_timer.config(text="✨ HORA DE IR EMBORA! ✨")
                self.alert_shown = False
                self.bouncing_enabled = False
                self.btn_toggle_bounce.config(text="Iniciar Bouncing")
            else:
                if restante <= datetime.timedelta(minutes=10):
                    if not self.alert_shown:
                        self.alert_shown = True
                    self.bouncing_enabled = True
                    self.btn_toggle_bounce.config(text="Parar Bouncing")

                horas, resto = divmod(int(restante.total_seconds()), 3600)
                minutos, segundos = divmod(resto, 60)
                texto = f"{horas:02}:{minutos:02}:{segundos:02}"
                self.label_timer.config(text=texto)

            time.sleep(1)

    def mover_janela(self):
        if self.bouncing_enabled:
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()

            hit_edge_x = False
            hit_edge_y = False

            if self.pos_x + LARGURA_JANELA >= screen_w or self.pos_x <= 0:
                self.vel_x = -self.vel_x
                hit_edge_x = True

            if self.pos_y + ALTURA_JANELA >= screen_h or self.pos_y <= 0:
                self.vel_y = -self.vel_y
                hit_edge_y = True

            self.pos_x += self.vel_x
            self.pos_y += self.vel_y

            self.root.geometry(f"{LARGURA_JANELA}x{ALTURA_JANELA}+{self.pos_x}+{self.pos_y}")

            if hit_edge_x or hit_edge_y:
                self.tocar_som()

        self.root.after(10, self.mover_janela)

    def tocar_som(self):
        if self.som and self.som_ativo:
            self.som.play()

    def animar_brilho(self):
        brilho = 155 + int(100 * abs(self.brilho_valor / 100))
        cor_hex = f"#{brilho:02x}{80:02x}00"

        self.label_info.config(bg=cor_hex)
        self.label_timer.config(bg=cor_hex)
        self.btn_voltar.config(bg=cor_hex, activebackground=cor_hex)
        self.btn_toggle_bounce.config(bg=cor_hex, activebackground=cor_hex)
        self.btn_toggle_sound.config(bg=cor_hex, activebackground=cor_hex)

        self.brilho_valor += self.brilho_direcao * 5
        if self.brilho_valor >= 100 or self.brilho_valor <= 0:
            self.brilho_direcao *= -1

        self.root.after(50, self.animar_brilho)

def escolher_horario_saida(root, callback):
    hoje = datetime.datetime.today().weekday()

    if hoje == 4:
        callback("17:00")
        return

    janela_opcao = tk.Toplevel(root)
    janela_opcao.title("Escolha o horário de saída")
    janela_opcao.geometry("250x100")
    janela_opcao.resizable(False, False)
    janela_opcao.grab_set()
    janela_opcao.attributes("-topmost", True)

    label = tk.Label(janela_opcao, text="Escolha o horário de saída:")
    label.pack(pady=5)

    def selecionar(horario):
        janela_opcao.destroy()
        callback(horario)

    btn_17 = tk.Button(janela_opcao, text="17:00", width=10, command=lambda: selecionar("17:00"))
    btn_17.pack(side="left", expand=True, padx=10, pady=10)

    btn_18 = tk.Button(janela_opcao, text="18:00", width=10, command=lambda: selecionar("18:00"))
    btn_18.pack(side="right", expand=True, padx=10, pady=10)

def main():
    root = tk.Tk()
    root.withdraw()

    def iniciar_app(horario_escolhido):
        root.deiconify()
        app = DVDApp(root, horario_escolhido, voltar_callback=lambda: escolher_horario_saida(root, iniciar_app))

    escolher_horario_saida(root, iniciar_app)
    root.mainloop()

if __name__ == "__main__":
    main()
