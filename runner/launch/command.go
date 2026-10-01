// Package launch builds and runs the command that executes one job on one host.
package launch

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"sort"
	"strings"

	"github.com/VivianSobers/StaleHand/runner/hosts"
	"github.com/VivianSobers/StaleHand/runner/matrix"
)

func shellQuote(s string) string {
	return "'" + strings.ReplaceAll(s, "'", `'\''`) + "'"
}

// quoteDir quotes a directory but leaves a leading ~/ for the remote shell to expand.
func quoteDir(d string) string {
	if strings.HasPrefix(d, "~/") {
		return "~/" + shellQuote(d[2:])
	}
	return shellQuote(d)
}

// RemoteCommand is the shell command run on the host. The job travels base64-encoded so no quoting can break it.
func RemoteCommand(h hosts.Host, j matrix.Job) string {
	spec, _ := json.Marshal(j)
	var b strings.Builder
	fmt.Fprintf(&b, "cd %s && ", quoteDir(h.Workdir))
	if len(h.Env) > 0 {
		keys := make([]string, 0, len(h.Env))
		for k := range h.Env {
			keys = append(keys, k)
		}
		sort.Strings(keys)
		b.WriteString("env ")
		for _, k := range keys {
			fmt.Fprintf(&b, "%s=%s ", k, shellQuote(h.Env[k]))
		}
	}
	fmt.Fprintf(&b, "%s -m stalehand run-job --job %s --out %s", shellQuote(h.Python),
		shellQuote(base64.StdEncoding.EncodeToString(spec)), shellQuote(fmt.Sprintf("runs/%s/%s", j.Matrix, j.ID)))
	return b.String()
}

// Argv runs the command locally through sh, or remotely through ssh without prompting for passwords.
func Argv(h hosts.Host, command string) []string {
	if h.SSH == "" {
		return []string{"sh", "-c", command}
	}
	return []string{"ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", h.SSH, command}
}
