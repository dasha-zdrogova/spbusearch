package service

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"

	"cli.go/config"
	"cli.go/model"
)

type Service struct {
	url string
}

func NewService() Service {
	return Service{url: fmt.Sprintf("%v:%v/api", config.HOST, config.PORT)}
}

func (s Service) Search(text model.UsersRequest) ([]model.UsersResponse, error) {
	resp, err := http.Get(fmt.Sprintf("http://%v/search?search_str=%v", s.url, url.QueryEscape(text.Text)))
	if err != nil {
		log.Fatal(err)
		return nil, err
	}
	var unm []model.UsersResponse
	rawBytes, readErr := io.ReadAll(resp.Body)
	if readErr != nil {
		log.Fatal(readErr)
		return nil, err
	}

	// fmt.Println(string(rawBytes))

	unmErr := json.Unmarshal(rawBytes, &unm)
	if unmErr != nil {
		log.Fatal(unmErr)
		return nil, err
	}

	return unm, nil
}