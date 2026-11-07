# BentoML Exam

## About

BentoML exam completed by Uwe Rosner as part of the Liora MLOps training.

## Development information

Prerequisites: [`uv`](https://docs.astral.sh/uv/), `make`, `curl`, Docker and
[`jq`](https://jqlang.org/) (used by the Makefile to extract the JWT token,
e.g. `sudo apt install jq`).

```bash
uv sync           # install Python 3.12 and all dependencies
make prepare      # clean and split the data into data/processed/
make train        # train the model, save it as admission_lr in the BentoML model store
make serve        # start the API on port 3000 (keep running, use a second terminal)
make predict      # log in and request a sample prediction
uv run pytest -v  # run the API tests against the running service
```

Test credentials: `user123` / `password123`. The tests use
`http://localhost:3000` by default, override with `API_URL=... uv run pytest -v`.
