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

// Service represents a client for the API service
type Service struct {
	url string
}

// NewService creates a new Service client with the configured URL
func NewService() Service {
	return Service{url: fmt.Sprintf("%v:%v/api", config.HOST, config.PORT)}
}

func GenerateSearchString(s Service, req model.UsersRequest) string {
	searchString := fmt.Sprintf("http://%v/search?search_str=%v", s.url, url.QueryEscape(req.Text))
	if req.Level != "" {
		searchString = fmt.Sprintf("%v&level=%v", searchString, req.Level)
	}
	if req.Code != "" {
		searchString = fmt.Sprintf("%v&code=%v", searchString, req.Code)
	}
	if req.Name != "" {
		searchString = fmt.Sprintf("%v&name=%v", searchString, req.Name)
	}
	if req.Field != "" {
		searchString = fmt.Sprintf("%v&field=%v", searchString, req.Field)
	}
	return searchString
}

// Search sends a search request to the API service and returns the search results
func (s Service) Search(req model.UsersRequest) ([]model.UsersResponse, error) {
	searchString := GenerateSearchString(s, req)
	log.Print(searchString)
	resp, err := http.Get(searchString)
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

	unmErr := json.Unmarshal(rawBytes, &unm)
	if unmErr != nil {
		log.Fatal(unmErr)
		return nil, err
	}

	return unm, nil
}
