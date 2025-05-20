import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import datetime
import threading
import time

LARGURA_JANELA = 400
ALTURA_JANELA = 150
VELOCIDADE = 5
IMAGEM_CAMINHO = "bannerIEZ.png"

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

        # Define tamanho da janela
        self.root.geometry(f"{LARGURA_JANELA}x{ALTURA_JANELA}+{self.pos_x}+{self.pos_y}")

        # Imagem de fundo
        try:
            img = Image.open(IMAGEM_CAMINHO).resize((LARGURA_JANELA, ALTURA_JANELA))
            self.bg_image = ImageTk.PhotoImage(img)
            self.label_image = tk.Label(root, image=self.bg_image)
            self.label_image.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print("Erro ao carregar imagem:", e)

        # Labels sobre a imagem
        self.label_info = tk.Label(
            root,
            text="Tempo restante para ir embora:",
            fg="white",
            bg="#ff6600",  # cor parecida com o fundo laranja
            font=("Arial", 10, "bold")
        )
        self.label_info.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

        self.label_timer = tk.Label(
            root, text="Calculando...",
            fg="white", bg="black", font=("Arial", 16, "bold")
        )
        self.label_timer.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        # Botão para voltar à escolha do horário
        self.btn_voltar = tk.Button(root, text="Voltar", command=self.voltar)
        self.btn_voltar.place(relx=0.25, rely=0.75, anchor=tk.CENTER)

        # Botão para iniciar/parar bouncing
        self.btn_toggle_bounce = tk.Button(root, text="Parar Bouncing", command=self.toggle_bouncing)
        self.btn_toggle_bounce.place(relx=0.75, rely=0.75, anchor=tk.CENTER)

        threading.Thread(target=self.atualizar_tempo, daemon=True).start()
        self.mover_janela()

    def voltar(self):
        # Destrói a janela atual e chama o callback para reabrir escolha de horário
        self.root.withdraw()
        self.voltar_callback()

    def toggle_bouncing(self):
        self.bouncing_enabled = not self.bouncing_enabled
        if self.bouncing_enabled:
            self.btn_toggle_bounce.config(text="Parar Bouncing")
        else:
            self.btn_toggle_bounce.config(text="Iniciar Bouncing")

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

            if self.pos_x + LARGURA_JANELA >= screen_w or self.pos_x <= 0:
                self.vel_x = -self.vel_x
            if self.pos_y + ALTURA_JANELA >= screen_h or self.pos_y <= 0:
                self.vel_y = -self.vel_y

            self.pos_x += self.vel_x
            self.pos_y += self.vel_y

            self.root.geometry(f"{LARGURA_JANELA}x{ALTURA_JANELA}+{self.pos_x}+{self.pos_y}")

        self.root.after(30, self.mover_janela)


def escolher_horario_saida(root, callback):
    hoje = datetime.datetime.today().weekday()  # 0 = segunda, 4 = sexta

    if hoje == 4:  # sexta-feira
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
    root.withdraw()  # Esconde temporariamente

    def iniciar_app(horario_escolhido):
        root.deiconify()
        # Passa a função para reabrir escolha de horário quando o botão voltar for pressionado
        app = DVDApp(root, horario_escolhido, voltar_callback=lambda: escolher_horario_saida(root, iniciar_app))

    escolher_horario_saida(root, iniciar_app)
    root.mainloop()

if __name__ == "__main__":
    main()
