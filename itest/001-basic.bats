#!/usr/bin/env bats   -*- bats -*-
#
# basic tests
#

load helpers

@test "user create" {
    expected_rc=0 run_helper curl -k --location --silent --header "Content-Type: application/json" --data '{"user_name":"hoge","email":"hoge@example.com","password":"hogepass","is_active":true,"is_superuser":false}' http://nginx/users.v1.UsersService/Create
    json="$output"
    assert_json "$json" ".id" =~ "^[0-9]+" "seq id"
    assert_json "$json" ".userName" =~ "hoge" "userName"
    assert_json "$json" ".email" =~ "hoge@example.com" "email"
    assert_json "$json" ".password" =~ "hogepass" "password"
    assert_json "$json" ".isActive" =~ "true" "isActive"
}
