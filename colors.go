package main

import (
	"image/color"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/theme"
)

// Sua struct de tema personalizado
type meuTema struct{}

func (m meuTema) Color(name fyne.ThemeColorName, variant fyne.ThemeVariant) color.Color {
	if name == theme.ColorNameForeground { // Cor do texto principal
		// Mude para branco para melhor contraste com sua imagem
		return color.White // fyne.io/fyne/v2/theme.PrimaryColorNamed("#FFFFFF") ou color.NRGBA{R: 255, G: 255, B: 255, A: 255}
	}
	// Para o fundo da janela, se você quiser que a janela em si seja escura:
	// if name == theme.ColorNameBackground {
	//  return color.NRGBA{R: 30, G: 30, B: 30, A: 255} // Um cinza escuro
	// }

	// Para outras cores, use o padrão do tema escuro (ou claro, se preferir)
	// Se o texto for branco, o tema escuro como base funciona bem.
	return theme.DarkTheme().Color(name, variant)
}

// ... os outros métodos do tema (Font, Icon, Size) permanecem os mesmos ...
func (m meuTema) Font(style fyne.TextStyle) fyne.Resource {
	return theme.DarkTheme().Font(style)
}

func (m meuTema) Icon(name fyne.ThemeIconName) fyne.Resource {
	return theme.DarkTheme().Icon(name)
}

func (m meuTema) Size(name fyne.ThemeSizeName) float32 {
	return theme.DarkTheme().Size(name)
}
