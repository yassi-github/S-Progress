package users

import (
	"context"

	"github.com/yassi-github/s-progress/domain/entity"
)

type Repository interface {
	Insert(ctx context.Context, user *entity.User) (id int32, err error)
	Select(ctx context.Context, id string) (*entity.User, error)
	SelectAll(ctx context.Context) ([]*entity.User, error)
}

// impl in "infra/repository/users/v1/repository.go"
