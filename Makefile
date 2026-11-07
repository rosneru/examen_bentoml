.PHONY: prepare train serve token predict test-api

PORT ?= 3000
SERVICE ?= src.service:AdmissionService
BASE_URL ?= http://127.0.0.1:$(PORT)

prepare: ## Clean the raw data and split it into train/test sets
	uv run python src/prepare_data.py

train: ## Train the model and save it to the BentoML model store
	uv run python src/train_model.py

serve: ## Start the prediction API
	uv run bentoml serve $(SERVICE) --port $(PORT)

token: ## Log in and print the JWT token
	@curl -s -X POST "$(BASE_URL)/login" \
		-H "Content-Type: application/json" \
		-d '{"credentials":{"username":"user123","password":"password123"}}' | jq -r '.token'

predict: ## Log in and request a prediction (start the API first with 'make serve')
	@token=$$(curl -s -X POST "$(BASE_URL)/login" \
		-H "Content-Type: application/json" \
		-d '{"credentials":{"username":"user123","password":"password123"}}' | jq -r '.token'); \
	curl -s -X POST "$(BASE_URL)/predict" \
		-H "Content-Type: application/json" \
		-H "Authorization: Bearer $$token" \
		-d '{"input_data":{"gre_score":335,"toefl_score":118,"university_rating":5,"sop":4.5,"lor":4.5,"cgpa":9.6,"research":true}}'; \
	echo

test-api: predict
