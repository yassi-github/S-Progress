package users

import (
	"context"

	"github.com/yassi-github/s-progress/domain/entity"
	"github.com/yassi-github/s-progress/domain/repository/users/v1"
)

type repository struct{}

func New() users.Repository {
	return &repository{}
}

func (r *repository) Insert(_ context.Context, user *entity.User) (id int32, err error) {
	// TODO: impl
	return 0, nil
}

func (r *repository) Select(_ context.Context, id string) (*entity.User, error) {
	// TODO: impl
	return nil, nil
}

func (r *repository) SelectAll(_ context.Context) ([]*entity.User, error) {
	// TODO: impl
	return nil, nil
}
