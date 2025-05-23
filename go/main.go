package main

import (
	"fmt"
	"image/color"
	"time"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/widget"
)

// Defina o horário de saída aqui (formato HH:MM)
const horarioSaida = "17:00" // Seu horário de saída
const imagePath = "./bannerIEZ.png"

func main() {
	a := app.New()

	a.Settings().SetTheme(&meuTema{})

	w := a.NewWindow("Fim do Turno") // Título da janela

	// Define que a janela não pode ser redimensionada pelo usuário
	w.SetFixedSize(true) // Considere remover ou ajustar isso se a imagem tiver um tamanho diferente

	// Cria um rótulo para exibir o tempo restante
	tempoRestanteLabel := widget.NewLabel("Calculando...")
	tempoRestanteLabel.Alignment = fyne.TextAlignCenter       // Centraliza o texto
	tempoRestanteLabel.TextStyle = fyne.TextStyle{Bold: true} // Opcional: Deixar o texto em negrito

	// Cria os rótulos que ficarão sobre a imagem
	textoFixoLabel := widget.NewLabel("Tempo restante para ir embora:")
	textoFixoLabel.Alignment = fyne.TextAlignCenter
	textoFixoLabel.TextStyle = fyne.TextStyle{Bold: true} // Opcional

	espacadorVertical := canvas.NewRectangle(color.Transparent)
	espacadorVertical.SetMinSize(fyne.NewSize(0, 20)) // Largura 0 (não ocupa espaço horizontal), Altura 10 pixels

	// Container para os textos (para que fiquem centralizados e um sobre o outro)
	textContainer := container.NewVBox(
		textoFixoLabel,
		espacadorVertical,
		tempoRestanteLabel,
	)

	textWithBackground := container.NewStack(
		// Retângulo de fundo. Ajuste a cor e a transparência (valor A de Alpha).
		// RGBA: R=Red, G=Green, B=Blue, A=Alpha (0=transparente, 255=opaco)
		canvas.NewRectangle(color.NRGBA{R: 0, G: 0, B: 0, A: 150}), // Preto semi-transparente (A:150 de 255)
		container.NewPadded(textContainer),                         // Adiciona padding ao redor do VBox de textos
	)

	img := canvas.NewImageFromFile(imagePath)
	if img == nil {
		// Se a imagem não puder ser carregada, você pode mostrar um erro ou usar um placeholder
		fmt.Println("Erro ao carregar a imagem:", imagePath)
		// Como fallback, podemos criar um retângulo colorido ou deixar sem imagem
		// Por exemplo, um retângulo cinza:
		// fallbackRect := canvas.NewRectangle(color.Gray{Y: 50})
		// fallbackRect.SetMinSize(fyne.NewSize(300, 100)) // Defina um tamanho mínimo
		// img = fallbackRect // Isso não é um canvas.Image, então precisa de ajuste
		// Neste caso, é mais simples prosseguir sem a imagem se ela falhar
	} else {
		img.FillMode = canvas.ImageFillStretch // Ou ImageFillContain, ImageFillOriginal, etc.
		// Se quiser que a imagem não seja muito pequena, pode definir um tamanho mínimo para ela.
		// img.SetMinSize(fyne.NewSize(400, 150)) // Exemplo de tamanho
	}

	var content fyne.CanvasObject
	if img != nil {
		// Centralize o container de texto COM fundo sobre a imagem
		centeredTextWithBackground := container.NewCenter(textWithBackground)
		content = container.NewStack(
			img,                        // Imagem no fundo
			centeredTextWithBackground, // Textos com seu próprio fundo, centralizados por cima
		)
	} else {
		// Fallback se a imagem não carregar: apenas os textos (agora com seu fundo)
		content = container.NewCenter(textWithBackground)
	}

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
