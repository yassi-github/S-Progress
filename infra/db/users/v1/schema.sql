create table users (
  id serial primary key,
  username text not null,
  email text,
  hashed_password text,
  is_active boolean,
  is_superuser boolean
);
