package entity

type User struct {
	UserName    string
	Email       string
	Password    string
	IsActive    bool
	IsSuperuser bool
}

type UserWithId struct {
	Id   int32
	User *User
}
