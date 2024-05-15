package main

import (
	"fmt"
	"log"
	"os"
	"strings"

	"cli.go/config"
	"cli.go/model"
	"cli.go/service"
	cli "github.com/urfave/cli/v2"
)

var s = service.NewService()

func main() {
	var text string
	var level string
	var code string
	var name string
	var field string
	app := &cli.App{
		Name:  "Spbusearch CLI",
		Usage: "Need to write",
		Commands: []*cli.Command{
			{
				Name:    "search",
				Aliases: []string{"s"},
				Action: func(_ *cli.Context) error {
					request := model.UsersRequest{
						Text:  text,
						Level: level,
						Code:  code,
						Name:  name,
						Field: field,
					}
					slice, err := s.Search(request)
					if err != nil {
						log.Fatal(err)
					}
					for _, note := range slice {
						fmt.Println()
						fmt.Println(config.Green + note.Title + config.Reset)
						fmt.Println(config.Purple + note.URL + config.Reset)
						fmt.Println()

						parts := strings.Split(note.Preview, "<b>")
						fmt.Print(strings.ReplaceAll(parts[0], "\n", ""))

						for _, part := range parts[1:] {
							subParts := strings.Split(part, "</b>")

							text = strings.ReplaceAll(subParts[0], "\n", "")
							fmt.Print(config.Bold + config.Yellow + text + config.Reset)

							text = strings.ReplaceAll(subParts[1], "\n", "")
							fmt.Print(text)
						}
						fmt.Println()
						fmt.Println()
					}
					return nil
				},
				Flags: []cli.Flag{
					&cli.StringFlag{
						Name:        "text",
						Usage:       "text that need to searching",
						Destination: &text,
						Required:    true,
					},
					&cli.StringFlag{
						Name:        "level",
						Aliases:     []string{"l"},
						Usage:       "Filter for education programm level",
						Destination: &level,
						Required:    false,
					},
					&cli.StringFlag{
						Name:        "code",
						Aliases:     []string{"c"},
						Usage:       "Filter for education programm code",
						Destination: &code,
						Required:    false,
					},
					&cli.StringFlag{
						Name:        "name",
						Aliases:     []string{"n"},
						Usage:       "Filter for education programm name",
						Destination: &name,
						Required:    false,
					},
					&cli.StringFlag{
						Name:        "field",
						Aliases:     []string{"f"},
						Usage:       "Filter for education programm field",
						Destination: &field,
						Required:    false,
					},
				},
			},
		},
	}

	if err := app.Run(os.Args); err != nil {
		log.Fatal(err)
	}
}
