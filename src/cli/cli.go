package main

import (
	"fmt"
	"log"
	"os"

	"cli.go/model"
	"cli.go/service"
	"github.com/urfave/cli/v2"
)

var s = service.NewService()

func main() {
	var text string
	app := &cli.App {
		Name: "Spbusearch CLI",
		Usage: "Need to write",
		Flags: []cli.Flag{
			&cli.StringFlag{
				Name: "text", 
				Usage: "text that need to searching",
				Destination: &text,
			},
		},
		// Action: func (ctx *cli.Context) error {
		// 	fmt.Println("Hello")
		// 	return nil
		// },
		Commands: []*cli.Command{
			{
				Name: "search",
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
						fmt.Println(note.Title)
						fmt.Println(note.Url)
						fmt.Println("\n")
						fmt.Println(note.Preview)
						fmt.Println("\n")
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