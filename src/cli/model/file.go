package model

type File struct {
	Url     string
	Title   string
	Preview string
}

type UsersRequest struct {
	Text string
}

type UsersResponse struct {
	Url     string `json:"url"`
	Title   string `json:"title"`
	Preview string `json:"preview"`
}
