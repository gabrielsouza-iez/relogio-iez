package main

import (
	"fmt"
	"time"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/widget"
)

// Defina o horário de saída aqui (formato HH:MM)
const horarioSaida = "17:00" // Seu horário de saída

func main() {
	a := app.New()
	w := a.NewWindow("Fim do Turno") // Título da janela

	// Define que a janela não pode ser redimensionada pelo usuário
	w.SetFixedSize(true)

	// Cria um rótulo para exibir o tempo restante
	tempoRestanteLabel := widget.NewLabel("Calculando...")
	tempoRestanteLabel.Alignment = fyne.TextAlignCenter // Centraliza o texto

	content := container.NewVBox(
		widget.NewLabel("Tempo restante para ir embora:"), // Texto fixo
		tempoRestanteLabel, // O rótulo que atualiza
	)

	w.SetContent(content)

	// Variável para controlar se o alerta de 10 minutos já foi exibido hoje
	var alertShown bool = false

	// Cria um goroutine para atualizar o relógio a cada segundo
	go func() {
		// Parseia o horário de saída definido
		horarioSaidaTime, err := time.Parse("15:04", horarioSaida)
		if err != nil {
			// Chamada Fyne dentro de fyne.Do
			fyne.Do(func() {
				tempoRestanteLabel.SetText(fmt.Sprintf("Erro ao definir horário: %v", err))
			})
			return // Sai da goroutine se houver erro
		}

		// Calcula o tempo de saída para hoje, combinando data atual com horário definido
		agora := time.Now()
		horarioSaidaHoje := time.Date(agora.Year(), agora.Month(), agora.Day(), horarioSaidaTime.Hour(), horarioSaidaTime.Minute(), 0, 0, agora.Location())

		// Se o horário de saída de hoje já passou, calcula para amanhã
		if agora.After(horarioSaidaHoje) {
			horarioSaidaHoje = horarioSaidaHoje.Add(24 * time.Hour)
		}

		// Loop para atualizar o tempo a cada segundo
		ticker := time.NewTicker(time.Second)
		defer ticker.Stop()

		for range ticker.C {
			agora := time.Now()
			// Calcula a duração até o horário de saída
			tempoFalta := horarioSaidaHoje.Sub(agora)

			// --- Lógica do Alerta de 10 minutos ---
			// Verifica se faltam 10 minutos ou menos E se o alerta ainda não foi mostrado E se o tempoFalta é positivo
			if !alertShown && tempoFalta > 0 && tempoFalta <= 10*time.Minute {
				// Chamada Fyne (ShowInformation) dentro de fyne.Do
				fyne.Do(func() {
					dialog.ShowInformation("Atenção!", "Faltam menos de 10 minutos para ir embora!", w)
				})
				alertShown = true // Marca que o alerta foi mostrado
			}
			// --- Fim da Lógica do Alerta ---

			// Se o tempo acabou (ou passou), exibe "Hora de ir!"
			if tempoFalta <= 0 {
				// Chamada Fyne (SetText) dentro de fyne.Do
				fyne.Do(func() {
					tempoRestanteLabel.SetText("✨ HORA DE IR EMBORA! ✨")
				})
				// Quando a hora de ir chega, resetamos o alerta para que ele funcione no dia seguinte
				alertShown = false
				// Se você quiser que a contagem pare e fique em "Hora de ir!", descomente a linha abaixo:
				// ticker.Stop()
				// return // Se descomentar o Stop(), descomente o return para sair da goroutine
			} else {
				// Formata a duração para Horas, Minutos e Segundos
				segundosTotais := int(tempoFalta.Seconds())
				horas := segundosTotais / 3600
				minutos := (segundosTotais % 3600) / 60
				segundos := segundosTotais % 60

				tempoStr := fmt.Sprintf("%02d:%02d:%02d", horas, minutos, segundos)
				// Chamada Fyne (SetText) dentro de fyne.Do
				fyne.Do(func() {
					tempoRestanteLabel.SetText(tempoStr)
				})
			}
		}
	}()

	// Mostra a janela e executa o loop principal da aplicação GUI
	w.ShowAndRun()
}
