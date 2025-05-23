import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import datetime
import threading
import time
import os
import json
import requests
import argparse

LARGURA_JANELA = 400
ALTURA_JANELA = 150
VELOCIDADE = 15
IMAGEM_CAMINHO = "bannerIEZ.png"
SOM_PATH = "som-do-zap-zap-estourado.mp3"

config_path = os.path.join(os.path.dirname(__file__), "config.json")
with open(config_path, "r") as f:
    config = json.load(f)

MEU_NOME = config["meu_nome"]
SERVIDOR = config["servidor"]

class DVDApp:
    def __init__(self, root, horario_saida, som_ativado=True):
        self.root = root
        self.horario_saida = horario_saida
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        self.pos_x = root.winfo_screenwidth()
        self.pos_y = 100
        self.vel_x = -VELOCIDADE
        self.vel_y = VELOCIDADE
        self.bouncing_enabled = False
        self.exibindo = False
        self.som_ativado = som_ativado

        self.root.geometry(f"{LARGURA_JANELA}x{ALTURA_JANELA}+{self.pos_x}+{self.pos_y}")

        try:
            img = Image.open(IMAGEM_CAMINHO).resize((LARGURA_JANELA, ALTURA_JANELA))
            self.bg_image = ImageTk.PhotoImage(img)
            self.label_image = tk.Label(root, image=self.bg_image)
            self.label_image.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print("Erro ao carregar imagem:", e)

        self.label_timer = tk.Label(root, text="Calculando...", fg="white", bg="black", font=("Arial", 16, "bold"))
        self.label_timer.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        if self.som_ativado:
            try:
                import pygame
                pygame.mixer.init()
                self.som = pygame.mixer.Sound(SOM_PATH) if os.path.exists(SOM_PATH) else None
            except Exception as e:
                print("Erro ao carregar som:", e)
                self.som = None
        else:
            self.som = None

        threading.Thread(target=self.atualizar_tempo, daemon=True).start()
        self.mover_janela()
        self.checar_se_deve_exibir()

    def atualizar_tempo(self):
        saida = datetime.datetime.strptime(self.horario_saida, "%H:%M").time()
        while True:
            agora = datetime.datetime.now()
            saida_hoje = datetime.datetime.combine(agora.date(), saida)
            if agora > saida_hoje:
                saida_hoje += datetime.timedelta(days=1)

            restante = saida_hoje - agora
            if restante.total_seconds() <= 0:
                texto = "✨ HORA DE IR EMBORA! ✨"
            else:
                horas, resto = divmod(int(restante.total_seconds()), 3600)
                minutos, segundos = divmod(resto, 60)
                texto = f"{horas:02}:{minutos:02}:{segundos:02}"
            self.label_timer.config(text=texto)
            time.sleep(1)

    def mover_janela(self):
        if self.bouncing_enabled:
            self.pos_x += self.vel_x
            self.pos_y += self.vel_y

            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()

            if self.pos_y <= 0 or self.pos_y + ALTURA_JANELA >= screen_h:
                self.vel_y = -self.vel_y
            if self.pos_x + LARGURA_JANELA < 0:
                self.root.withdraw()
                self.bouncing_enabled = False
                self.exibindo = False
                self.notificar_saida()
                return

            self.root.geometry(f"{LARGURA_JANELA}x{ALTURA_JANELA}+{self.pos_x}+{self.pos_y}")
        self.root.after(20, self.mover_janela)

    def tocar_som(self):
        if self.som:
            self.som.play()

    def checar_se_deve_exibir(self):
        try:
            r = requests.get(f"{SERVIDOR}/quem_deve_exibir", params={"host": MEU_NOME})
            if r.ok:
                data = r.json()
                if data.get("exibir") and not self.exibindo:
                    self.exibindo = True
                    self.pos_x = self.root.winfo_screenwidth()
                    self.root.deiconify()
                    self.bouncing_enabled = True
                    self.tocar_som()
        except Exception as e:
            print("Erro ao checar exibição:", e)
        self.root.after(1000, self.checar_se_deve_exibir)

    def notificar_saida(self):
        try:
            requests.post(f"{SERVIDOR}/janela_saiu", json={"host": MEU_NOME})
        except Exception as e:
            print("Erro ao notificar saída:", e)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sem-som", action="store_true", help="Inicia o cliente sem tocar som")
    args = parser.parse_args()

    root = tk.Tk()
    root.withdraw()
    DVDApp(root, "18:00", som_ativado=not args.sem_som)
    root.mainloop()

if __name__ == "__main__":
    main()
