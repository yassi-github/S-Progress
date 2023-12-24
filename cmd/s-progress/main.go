package main

import (
	"github.com/labstack/echo/v4"

	"github.com/yassi-github/s-progress/routers"
)

func main() {
	e := echo.New()
	e.Static("/static", "static")
	e.File("/", "static/html/index.html")

	routers.UserRoutes(e)

	e.Logger.Fatal(e.Start(":8000"))
}
