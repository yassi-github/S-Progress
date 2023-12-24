package users

// # insert用のrequest model。id(自動採番)は入力不要のため定義しない。
type UserCreate struct {
	Username     string
	Email        string
	Password     string
	Is_Active    bool
	Is_Superuser bool
}

// # update用のrequest model
type UserUpdate struct {
	Id           int
	Username     string
	Email        string
	Password     string
	Is_Active    bool
	Is_Superuser bool
}

// # select用のrequest model。selectでは、パスワード不要のため定義しない。
type UserSelect struct {
	Username     string
	Email        string
	Is_Active    bool
	Is_Superuser bool
}
