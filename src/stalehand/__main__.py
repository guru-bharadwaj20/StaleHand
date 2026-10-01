"""`python -m stalehand`, which is how the Go runner starts run-job on a host."""
import sys

from .cli import main

sys.exit(main())
