.PHONY: dev test seed build install frontend-install frontend-dev

# Backend
install:
	cd backend && pip install -r requirements.txt

dev:
	cd backend && uvicorn app.main:app --reload --port 3008

test:
	cd backend && python -m pytest tests/ -v --tb=short

seed:
	cd backend && python seed.py

build:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install && npm run build

# Frontend
frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev
