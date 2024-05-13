package main

import (
	"fmt"
	"log"
	"os"
	"strings"

	"cli.go/config"
	"cli.go/model"
	"cli.go/service"
	"github.com/urfave/cli/v2"
)

var s = service.NewService()

func main() {
	var text string
	app := &cli.App{
		Name:  "Spbusearch CLI",
		Usage: "Need to write",
		Flags: []cli.Flag{
			&cli.StringFlag{
				Name:        "text",
				Usage:       "text that need to searching",
				Destination: &text,
			},
		},
		// Action: func (ctx *cli.Context) error {
		// 	fmt.Println("Hello")
		// 	return nil
		// },
		Commands: []*cli.Command{
			{
				Name:    "search",
				Aliases: []string{"s"},
				Action: func(ctx *cli.Context) error {
					request := model.UsersRequest{
						Text: text,
					}
					slice, err := s.Search(request)
					if err != nil {
						log.Fatal(err)
					}
					for _, note := range slice {
						fmt.Println()
						fmt.Println(config.Green + note.Title + config.Reset)
						fmt.Println(config.Purple + note.Url + config.Reset)
						fmt.Println()

						parts := strings.Split(note.Preview, "<b>")
						fmt.Print(strings.ReplaceAll(parts[0], "\n", " "))

						for _, part := range parts[1:] {
							subParts := strings.Split(part, "</b>")

							text = strings.ReplaceAll(subParts[0], "\n", " ")
							fmt.Print(config.Bold + config.Yellow + text + config.Reset)

							text = strings.ReplaceAll(subParts[1], "\n", " ")
							fmt.Print(text)
						}
						fmt.Println()
						fmt.Println()
					}
					return nil
				},
			},
		},
	}

	if err := app.Run(os.Args); err != nil {
		log.Fatal(err)
	}
}
