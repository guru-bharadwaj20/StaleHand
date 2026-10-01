// stalerun plans, runs and reports StaleHand job sweeps.
//
//	stalerun plan    -matrix m.json -db runs.db
//	stalerun run     -db runs.db -hosts hosts.json [-logs logs]
//	stalerun status  -db runs.db
//	stalerun release -db runs.db -host gpu1
//	stalerun collect -db runs.db -hosts hosts.json -dest results/vivian-4090
package main

import (
	"context"
	"flag"
	"fmt"
	"io"
	"os"
	"os/signal"
	"sort"
	"syscall"

	"github.com/VivianSobers/StaleHand/runner/collect"
	"github.com/VivianSobers/StaleHand/runner/dispatch"
	"github.com/VivianSobers/StaleHand/runner/hosts"
	"github.com/VivianSobers/StaleHand/runner/launch"
	"github.com/VivianSobers/StaleHand/runner/matrix"
	"github.com/VivianSobers/StaleHand/runner/store"
)

func main() {
	if err := run(os.Args[1:], os.Stdout); err != nil {
		fmt.Fprintln(os.Stderr, "stalerun:", err)
		os.Exit(1)
	}
}

func run(args []string, out io.Writer) error {
	if len(args) == 0 {
		return fmt.Errorf("usage: stalerun plan|run|status|release|collect [flags]")
	}
	fs := flag.NewFlagSet(args[0], flag.ContinueOnError)
	db := fs.String("db", "runs.db", "job database")
	matrixPath := fs.String("matrix", "", "experiment matrix (plan)")
	hostsPath := fs.String("hosts", "runner/hosts.json", "host definitions (run)")
	logs := fs.String("logs", "logs", "job log directory (run)")
	host := fs.String("host", "", "host name (release)")
	dest := fs.String("dest", "results", "directory to copy finished runs into (collect)")
	if err := fs.Parse(args[1:]); err != nil {
		return err
	}
	st, err := store.Open(*db)
	if err != nil {
		return err
	}
	defer st.Close()
	switch args[0] {
	case "plan":
		f, err := os.Open(*matrixPath)
		if err != nil {
			return err
		}
		defer f.Close()
		m, err := matrix.Parse(f)
		if err != nil {
			return err
		}
		jobs := m.Expand()
		if err := st.Add(jobs); err != nil {
			return err
		}
		fmt.Fprintf(out, "planned %d jobs for %s\n", len(jobs), m.Name)
		return printStatus(st, out)
	case "run":
		hs, err := readHosts(*hostsPath)
		if err != nil {
			return err
		}
		ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
		defer stop()
		sum, err := dispatch.Dispatch(ctx, st, hs, launch.ExecRunner{LogDir: *logs}, out)
		fmt.Fprintf(out, "done %d, failed attempts %d\n", sum.Done, sum.Failed)
		for _, h := range hs { // jobs interrupted by Ctrl-C go back to pending
			st.Release(h.Name)
		}
		return err
	case "status":
		return printStatus(st, out)
	case "collect":
		hs, err := readHosts(*hostsPath)
		if err != nil {
			return err
		}
		placed, err := st.Finished()
		if err != nil {
			return err
		}
		sum := collect.All(placed, hs, *dest, collect.RunCommand)
		for _, p := range sum.Problems {
			fmt.Fprintln(out, "problem:", p)
		}
		fmt.Fprintf(out, "copied %d of %d finished jobs into %s\n", sum.Copied, len(placed), *dest)
		if len(sum.Problems) > 0 {
			return fmt.Errorf("%d jobs not collected", len(sum.Problems))
		}
		return nil
	case "release":
		n, err := st.Release(*host)
		if err != nil {
			return err
		}
		fmt.Fprintf(out, "released %d jobs from %s\n", n, *host)
		return nil
	}
	return fmt.Errorf("unknown command %q", args[0])
}

func readHosts(path string) ([]hosts.Host, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	return hosts.Parse(f)
}

func printStatus(st *store.Store, out io.Writer) error {
	c, err := st.Counts()
	if err != nil {
		return err
	}
	keys := make([]string, 0, len(c))
	for k := range c {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	for _, k := range keys {
		fmt.Fprintf(out, "%-8s %d\n", k, c[k])
	}
	return nil
}
