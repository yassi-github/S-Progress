package users

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
)

func TestListAll(t *testing.T) {
	// Setup
	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/users")

	// Assertions
	userJSONList := `[{"Username":"mockuser","Email":"user@mock.example.com","Is_Active":false,"Is_Superuser":true},{"Username":"mockuser","Email":"user@mock.example.com","Is_Active":false,"Is_Superuser":true}]
`
	if assert.NoError(t, ListAll(c)) {
		assert.Equal(t, http.StatusOK, rec.Code)
		assert.Equal(t, userJSONList, rec.Body.String())
	}
}
