package model

// UsersRequest represents the structure of the request made to the API service
type UsersRequest struct {
	Text  string
	Level string
	Code  string
	Name  string
	Field string
}

// UsersResponse represents the structure of the response received from the API service
type UsersResponse struct {
	URL     string `json:"url"`
	Title   string `json:"title"`
	Preview string `json:"preview"`
}
