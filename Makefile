SHELL := /bin/bash
.ONESHELL:		## so that the token is still set in the second curl command

PORT ?= 3000
URL  := http://localhost:$(PORT)

.PHONY: help prepare train serve test-api

help: ## Show available targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*## "}; {printf "  %-10s %s\n", $$1, $$2}'

prepare: ## Clean the raw data and split it into train/test sets
	uv run python src/prepare_data.py

train: ## Train the model and save it to the BentoML model store
	uv run python src/train_model.py

serve: ## Start the prediction API
	cd src && uv run bentoml serve service:AdmissionService --port $(PORT)

test-api: ## Log in and request a prediction (start the API first with 'make serve')
	token=$$(curl -s -X POST $(URL)/login \
		-H 'Content-Type: application/json' \
		-d '{"credentials": {"username": "user123", "password": "password123"}}' \
		| sed -E 's/.*"token": *"([^"]+)".*/\1/')
	curl -s -X POST $(URL)/predict \
		-H 'Content-Type: application/json' \
		-H "Authorization: Bearer $$token" \
		-d '{"input_data": {"gre_score": 335, "toefl_score": 118, "university_rating": 5, "sop": 4.5, "lor": 4.5, "cgpa": 9.6, "research": true}}'
	echo
