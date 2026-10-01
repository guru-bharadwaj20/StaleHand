// Package store keeps job status in SQLite so a crashed or interrupted sweep resumes where it stopped.
package store

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"time"

	"github.com/VivianSobers/StaleHand/runner/matrix"
	_ "modernc.org/sqlite"
)

const schema = `
CREATE TABLE IF NOT EXISTS jobs (
  id          TEXT PRIMARY KEY,
  matrix      TEXT NOT NULL,
  spec        TEXT NOT NULL,
  status      TEXT NOT NULL CHECK (status IN ('pending', 'running', 'done', 'failed')),
  host        TEXT,
  attempts    INTEGER NOT NULL DEFAULT 0,
  started_at  TEXT,
  finished_at TEXT,
  exit_code   INTEGER,
  error       TEXT
);
CREATE INDEX IF NOT EXISTS jobs_status ON jobs(status);`

// Store wraps the database. MaxAttempts bounds retries of failed jobs.
type Store struct {
	db          *sql.DB
	MaxAttempts int
}

func Open(path string) (*Store, error) {
	db, err := sql.Open("sqlite", path+"?_pragma=busy_timeout(5000)&_pragma=journal_mode(WAL)")
	if err != nil {
		return nil, err
	}
	db.SetMaxOpenConns(1)
	if _, err := db.Exec(schema); err != nil {
		db.Close()
		return nil, fmt.Errorf("store: %w", err)
	}
	return &Store{db: db, MaxAttempts: 3}, nil
}

func (s *Store) Close() error { return s.db.Close() }

func now() string { return time.Now().UTC().Format(time.RFC3339) }

// Add inserts new jobs as pending; jobs already present keep their status.
func (s *Store) Add(jobs []matrix.Job) error {
	tx, err := s.db.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()
	for _, j := range jobs {
		spec, _ := json.Marshal(j)
		if _, err := tx.Exec(`INSERT OR IGNORE INTO jobs (id, matrix, spec, status) VALUES (?, ?, ?, 'pending')`,
			j.ID, j.Matrix, string(spec)); err != nil {
			return err
		}
	}
	return tx.Commit()
}

// Claim marks up to n runnable jobs as running on host and returns them.
func (s *Store) Claim(host string, n int) ([]matrix.Job, error) {
	tx, err := s.db.Begin()
	if err != nil {
		return nil, err
	}
	defer tx.Rollback()
	rows, err := tx.Query(`SELECT id, spec FROM jobs
		WHERE status = 'pending' OR (status = 'failed' AND attempts < ?)
		ORDER BY attempts, id LIMIT ?`, s.MaxAttempts, n)
	if err != nil {
		return nil, err
	}
	var out []matrix.Job
	for rows.Next() {
		var id, spec string
		if err := rows.Scan(&id, &spec); err != nil {
			rows.Close()
			return nil, err
		}
		var j matrix.Job
		if err := json.Unmarshal([]byte(spec), &j); err != nil {
			rows.Close()
			return nil, err
		}
		out = append(out, j)
	}
	rows.Close()
	for _, j := range out {
		if _, err := tx.Exec(`UPDATE jobs SET status = 'running', host = ?, attempts = attempts + 1,
			started_at = ?, finished_at = NULL, exit_code = NULL, error = NULL WHERE id = ?`, host, now(), j.ID); err != nil {
			return nil, err
		}
	}
	return out, tx.Commit()
}

// Finish records a job's exit; non-zero exit codes mark it failed.
func (s *Store) Finish(id string, exitCode int, errMsg string) error {
	status := "done"
	if exitCode != 0 {
		status = "failed"
	}
	_, err := s.db.Exec(`UPDATE jobs SET status = ?, finished_at = ?, exit_code = ?, error = ? WHERE id = ?`,
		status, now(), exitCode, errMsg, id)
	return err
}

// Release returns a host's running jobs to pending, for when the host died or was stopped.
func (s *Store) Release(host string) (int64, error) {
	res, err := s.db.Exec(`UPDATE jobs SET status = 'pending', host = NULL WHERE status = 'running' AND host = ?`, host)
	if err != nil {
		return 0, err
	}
	return res.RowsAffected()
}

// Placed is a finished job and the host whose disk holds its run directory.
type Placed struct {
	Job  matrix.Job
	Host string
}

// Finished returns every done job, in id order.
func (s *Store) Finished() ([]Placed, error) {
	rows, err := s.db.Query(`SELECT spec, host FROM jobs WHERE status = 'done' ORDER BY id`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var out []Placed
	for rows.Next() {
		var spec, host string
		if err := rows.Scan(&spec, &host); err != nil {
			return nil, err
		}
		var p Placed
		if err := json.Unmarshal([]byte(spec), &p.Job); err != nil {
			return nil, err
		}
		p.Host = host
		out = append(out, p)
	}
	return out, rows.Err()
}

// Counts returns the number of jobs per status.
func (s *Store) Counts() (map[string]int, error) {
	rows, err := s.db.Query(`SELECT status, COUNT(*) FROM jobs GROUP BY status`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	out := map[string]int{}
	for rows.Next() {
		var st string
		var n int
		if err := rows.Scan(&st, &n); err != nil {
			return nil, err
		}
		out[st] = n
	}
	return out, rows.Err()
}
