package main

import (
	"context"
	"errors"
	"net/http"
	"os"
	"os/signal"
	"time"

	"github.com/jackc/pgx/v5"
	// "github.com/jackc/pgx/v5/pgtype"
	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"

	"github.com/rs/cors"

	users "github.com/yassi-github/s-progress/handler/users/v1"
	usersv1repository "github.com/yassi-github/s-progress/infra/repository/users/v1"
	"github.com/yassi-github/s-progress/log"
	usersv1interactor "github.com/yassi-github/s-progress/usecase/users/v1"

	"github.com/yassi-github/s-progress/gen/users/v1/usersv1protoconnect" // generated by protoc-gen-connect-go
)

func main() {
	os.Exit(run())
}

func run() int {
	const (
		exit_ok = 0
		exit_ng = 1
	)

	// DI
	logger := log.NewHandler(log.LevelInfo, log.WithJSONFormat())

	logger.InfoCtx(context.Background(), "starting", "s-progress app")

	// should we open db now?
	dbCtx := context.Background()
	// db conn info looks blank but is retrieved from env (https://www.postgresql.org/docs/11/libpq-envars.html).
	dbConnection, err := pgx.Connect(dbCtx, "")
	if err != nil {
		logger.ErrorCtx(dbCtx, "failed to connect db", "err", err)
		return exit_ng
	}
	defer dbConnection.Close(dbCtx)

	// shouldnt pass specific db typed connection?
	usersRepository := usersv1repository.New(dbConnection)
	usersInteractor := usersv1interactor.New(usersRepository)
	usersServer := users.New(logger, usersInteractor)

	mux := http.NewServeMux()

	// add handlers below.
	mux.Handle(usersv1protoconnect.NewUsersServiceHandler(usersServer))

	// use http2 but server setting (addr, handler) is set by http pkg.
	handler := cors.AllowAll().Handler(h2c.NewHandler(mux, &http2.Server{}))
	srv := &http.Server{
		Addr:    ":8000",
		Handler: handler,
	}

	// receive kill signal by context.
	// context.Background() create and init context.
	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt, os.Kill)
	defer cancel()

	// up http server.
	go func() {
		if err := srv.ListenAndServe(); !errors.Is(err, http.ErrServerClosed) {
			logger.ErrorCtx(ctx, "failed to ListenAndServe", "err", err)
		}
	}()

	// wait till context canceled.
	<-ctx.Done()

	// graceful shutdown with timeout.
	timeoutCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err := srv.Shutdown(timeoutCtx); err != nil {
		return exit_ng
	}
	return exit_ok
}