# integration test with bats

## Running tests

To run the tests locally in your sandbox, you can use one of these methods:
* bats ./test/001-basic.bats  # runs just the specified test
* bats ./test/                # runs all

### Run bats by Docker

Build bats image

```sh
docker build -t itest -f ./itest/Dockerfile ./itest/
```

Then run bats

```sh
# runs all
./build.sh itest
# runs just the specified test
./build.sh itest ./itest/001-basic.bats
```
