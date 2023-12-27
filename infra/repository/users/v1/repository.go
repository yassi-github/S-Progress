package users

import (
	"context"

	"github.com/jackc/pgx/v5"
	// "github.com/jackc/pgx/v5/pgtype"

	"github.com/yassi-github/s-progress/domain/entity"
	"github.com/yassi-github/s-progress/domain/repository/users/v1"
	db "github.com/yassi-github/s-progress/infra/db/users/v1"
)

type repository struct {
	dbConnection *pgx.Conn
}

func New(conn *pgx.Conn) users.Repository {
	return &repository{
		dbConnection: conn,
	}
}

func (r *repository) Insert(ctx context.Context, user *entity.User) (id int32, err error) {
	queries := db.New(r.dbConnection)
	createdUser, err := queries.CreateUser(ctx, db.CreateUserParams{
		Username:       user.UserName,
		Email:          &user.Email,
		HashedPassword: &user.Password,
		IsActive:       &user.IsActive,
		IsSuperuser:    &user.IsSuperuser,
	})
	if err != nil {
		return 0, err
	}
	return createdUser.ID, nil
}

func (r *repository) Select(_ context.Context, id string) (*entity.User, error) {
	// TODO: impl
	return nil, nil
}

func (r *repository) SelectAll(_ context.Context) ([]*entity.User, error) {
	// TODO: impl
	return nil, nil
}
