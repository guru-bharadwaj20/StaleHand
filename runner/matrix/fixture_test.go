package matrix

import (
	"encoding/base64"
	"encoding/json"
	"os"
	"testing"
)

// The Python side (stalehand run-job) decodes the same fixture, so both languages agree on the job format and ID.
func TestJobMatchesSharedFixture(t *testing.T) {
	raw, err := os.ReadFile("../../schema/fixtures/job.json")
	if err != nil {
		t.Fatal(err)
	}
	var fx struct {
		Job    Job    `json:"job"`
		Base64 string `json:"base64"`
	}
	if err := json.Unmarshal(raw, &fx); err != nil {
		t.Fatal(err)
	}
	if got := jobID(fx.Job); got != fx.Job.ID {
		t.Fatalf("jobID = %s, fixture says %s", got, fx.Job.ID)
	}
	enc, _ := json.Marshal(fx.Job)
	if got := base64.StdEncoding.EncodeToString(enc); got != fx.Base64 {
		t.Fatalf("encoding changed:\n%s", enc)
	}
}
