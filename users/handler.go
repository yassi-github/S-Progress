package users

import (
	"github.com/labstack/echo/v4"
	"net/http"
)

func ListAll(c echo.Context) error {
	mock_user_select_list := []UserSelect{
		UserSelect{
			Username:     "mockuser",
			Email:        "user@mock.example.com",
			Is_Active:    false,
			Is_Superuser: true,
		},
		UserSelect{
			Username:     "mockuser",
			Email:        "user@mock.example.com",
			Is_Active:    false,
			Is_Superuser: true,
		},
	}

	return c.JSON(http.StatusOK, mock_user_select_list)
}
