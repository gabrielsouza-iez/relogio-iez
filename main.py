import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import datetime
import threading
import time
import pygame
import os
import random

LARGURA_JANELA = 520  # Aumentado em 30% (400 * 1.3)
ALTURA_JANELA = 195   # Aumentado em 30% (150 * 1.3)
VELOCIDADE = 7
IMAGEM_CAMINHO = "bannerIEZ.png"

# Lista de imagens para alternar sequencialmente
IMAGENS_DISPONIVEIS = [
    "bannerIEZ.png",
    "image/daniel.png",
    "image/daniel2.png",
    "image/daniel3.png",
    "image/gabriel.png",
    "image/gabriel2.png",
    "image/guilherme.png",
    "image/gustavo.png",
    "image/murilo.png",
    "image/vitor.png",
    "image/william.png",
    "image/felipe.png",
    "image/felipe2.png",
    "image/elementor.png",
    "image/gustavoReacoes.png",
    "image/jamalBieber.png",
    "image/naruto.png",
    "image/jesusPastel.png",
    "image/bolsAlien.png",
    "image/callSaul.png",
    "image/cursedEgg.png"
]

# Lista de sons para alternar sequencialmente
SONS_DISPONIVEIS = [
    "sons/som-do-zap-zap-estourado.mp3",
    "sons/serra.mp3",
    "sons/zoeira-efeito-suspense.mp3",
    "sons/mola-boina-boing.mp3",
    "sons/luan-moto.mp3",
    "sons/efeito-sonoro-alerta.mp3",
    "sons/audio.mp3",
    "sons/cavalo-ratinho.mp3",
    "sons/efeito-sonoro-cutuco-correndo.mp3",
    "sons/ui-rodrigo-faro.mp3"
]

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

        # Sistema de seleção aleatória sem repetição para imagens
        self.imagens_disponiveis = IMAGENS_DISPONIVEIS.copy()
        self.imagens_usadas = []
        self.imagem_atual_caminho = random.choice(self.imagens_disponiveis)
        self.imagens_disponiveis.remove(self.imagem_atual_caminho)
        self.imagens_usadas.append(self.imagem_atual_caminho)

        # Sistema de seleção aleatória sem repetição para sons
        self.sons_disponiveis = SONS_DISPONIVEIS.copy()
        self.sons_usados = []
        self.som_atual_caminho = random.choice(self.sons_disponiveis)
        self.sons_disponiveis.remove(self.som_atual_caminho)
        self.sons_usados.append(self.som_atual_caminho)

        self.root.geometry(f"{LARGURA_JANELA}x{ALTURA_JANELA}+{self.pos_x}+{self.pos_y}")

        # Carrega a imagem inicial
        self.carregar_imagem()

        # Carrega o som inicial
        self.carregar_som()

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

        # Atalhos para aumentar/diminuir velocidade
        self.root.bind('<Up>', lambda e: self.aumentar_velocidade())
        self.root.bind('<Down>', lambda e: self.diminuir_velocidade())

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

            # Quando a janela encosta na borda, toca o som e seleciona uma nova imagem aleatória
            if hit_edge_x or hit_edge_y:
                self.tocar_som()
                self.proxima_imagem()  # Seleciona uma nova     imagem aleatória sem repetição
                self.proximo_som()     # Seleciona um novo som aleatório sem repetição

        self.root.after(10, self.mover_janela)

    def tocar_som(self):
        if self.som and self.som_ativo:
            self.som.play()

    def carregar_som(self):
        """Carrega o som atual"""
        try:
            if os.path.exists(self.som_atual_caminho):
                self.som = pygame.mixer.Sound(self.som_atual_caminho)
                print(f"Som carregado: {self.som_atual_caminho}")
            else:
                self.som = None
                print(f"Arquivo de som não encontrado: {self.som_atual_caminho}")
        except Exception as e:
            print(f"Erro ao carregar som {self.som_atual_caminho}:", e)
            self.som = None

    def proximo_som(self):
        """Seleciona um som aleatório sem repetição"""
        # Se todos os sons foram usados, reinicia o baralho
        if not self.sons_disponiveis:
            print("Todos os sons foram tocados! Reiniciando o baralho...")
            self.sons_disponiveis = SONS_DISPONIVEIS.copy()
            self.sons_usados.clear()
        
        # Seleciona um som aleatório dos disponíveis
        self.som_atual_caminho = random.choice(self.sons_disponiveis)
        self.sons_disponiveis.remove(self.som_atual_caminho)
        self.sons_usados.append(self.som_atual_caminho)
        
        print(f"Alterando para som: {self.som_atual_caminho}")
        print(f"Sons restantes: {len(self.sons_disponiveis)}")
        self.carregar_som()

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

    def carregar_imagem(self):
        """Carrega a imagem atual e atualiza o label"""
        try:
            img = Image.open(self.imagem_atual_caminho).resize((LARGURA_JANELA, ALTURA_JANELA))
            self.bg_image = ImageTk.PhotoImage(img)

            # Se o label já existe, atualiza a imagem
            if hasattr(self, 'label_image'):
                self.label_image.config(image=self.bg_image)
            else:
                # Cria o label da imagem pela primeira vez
                self.label_image = tk.Label(self.root, image=self.bg_image)
                self.label_image.place(x=0, y=0, relwidth=1, relheight=1)

        except Exception as e:
            print(f"Erro ao carregar imagem {self.imagem_atual_caminho}:", e)
            # Se falhar, tenta carregar uma nova imagem aleatória
            self.proxima_imagem()

    def proxima_imagem(self):
        """Seleciona uma imagem aleatória sem repetição"""
        # Se todas as imagens foram usadas, reinicia o baralho
        if not self.imagens_disponiveis:
            print("Todas as imagens foram mostradas! Reiniciando o baralho...")
            self.imagens_disponiveis = IMAGENS_DISPONIVEIS.copy()
            self.imagens_usadas.clear()
        
        # Seleciona uma imagem aleatória das disponíveis
        self.imagem_atual_caminho = random.choice(self.imagens_disponiveis)
        self.imagens_disponiveis.remove(self.imagem_atual_caminho)
        self.imagens_usadas.append(self.imagem_atual_caminho)
        
        print(f"Alterando para imagem: {self.imagem_atual_caminho}")
        print(f"Imagens restantes: {len(self.imagens_disponiveis)}")
        self.carregar_imagem()

    def aumentar_velocidade(self):
        # Aumenta a velocidade em 30%, mas se for 1 ou -1, vai para 2 ou -2
        if self.vel_x == 1:
            self.vel_x = 2
        elif self.vel_x == -1:
            self.vel_x = -2
        elif self.vel_x > 0:
            self.vel_x = max(1, round(self.vel_x * 1.3))
        else:
            self.vel_x = min(-1, round(self.vel_x * 1.3))
        if self.vel_y == 1:
            self.vel_y = 2
        elif self.vel_y == -1:
            self.vel_y = -2
        elif self.vel_y > 0:
            self.vel_y = max(1, round(self.vel_y * 1.3))
        else:
            self.vel_y = min(-1, round(self.vel_y * 1.3))
        print(f"Velocidade aumentada: vel_x={self.vel_x}, vel_y={self.vel_y}")

    def diminuir_velocidade(self):
        # Diminui a velocidade em 30%, mas nunca menor que 1 (ou -1)
        if self.vel_x > 0:
            self.vel_x = max(1, int(self.vel_x * 0.7))
        else:
            self.vel_x = min(-1, int(self.vel_x * 0.7))
        if self.vel_y > 0:
            self.vel_y = max(1, int(self.vel_y * 0.7))
        else:
            self.vel_y = min(-1, int(self.vel_y * 0.7))
        print(f"Velocidade diminuída: vel_x={self.vel_x}, vel_y={self.vel_y}")

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
