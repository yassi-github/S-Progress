package users

import (
	"context"

	"github.com/yassi-github/s-progress/domain/entity"
	usersv1repository "github.com/yassi-github/s-progress/domain/repository/users/v1"
)

type Interactor interface {
	Create(ctx context.Context, name, email, password string, is_active, is_superuser bool) (*entity.UserWithId, error)
	FindAll(ctx context.Context, name, email, password string, is_active, is_superuser bool) ([]*entity.User, error)
	Find(ctx context.Context, name, email, password string, is_active, is_superuser bool) (*entity.User, error)
	Update(ctx context.Context, name, email, password string, is_active, is_superuser bool) (*entity.User, error)
	Delete(ctx context.Context, name, email, password string, is_active, is_superuser bool) (*entity.User, error)
}

type interactor struct {
	usersRepository usersv1repository.Repository
}

func New(
	usersRepository usersv1repository.Repository,
) Interactor {
	return &interactor{
		usersRepository,
	}
}

func (i *interactor) Create(ctx context.Context, name, email, password string, is_active, is_superuser bool) (*entity.UserWithId, error) {
	user := &entity.User{
		UserName:    name,
		Email:       email,
		Password:    password,
		IsActive:    is_active,
		IsSuperuser: is_superuser,
	}
	id, err := i.usersRepository.Insert(ctx, user)
	if err != nil {
		return nil, err
	}
	userWithId := &entity.UserWithId{
		Id: id,
		User: user,
	}
	return userWithId, nil
}

func (i *interactor) FindAll(ctx context.Context, name, email, password string, is_active, is_superuser bool) ([]*entity.User, error) {
	return nil, nil
}
func (i *interactor) Find(ctx context.Context, name, email, password string, is_active, is_superuser bool) (*entity.User, error) {
	return nil, nil
}
func (i *interactor) Update(ctx context.Context, name, email, password string, is_active, is_superuser bool) (*entity.User, error) {
	return nil, nil
}
func (i *interactor) Delete(ctx context.Context, name, email, password string, is_active, is_superuser bool) (*entity.User, error) {
	return nil, nil
}
