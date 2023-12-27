-- name: CreateUser :one
insert into users (
  username,
  email,
  hashed_password,
  is_active,
  is_superuser
) values (
  $1, $2, $3, $4, $5
) returning *;
