package routers

import (
	"github.com/labstack/echo/v4"
	"github.com/yassi-github/s-progress/users"
)

func UserRoutes(e *echo.Echo) {
	e.GET("/users", users.ListAll)
}
