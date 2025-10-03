.PHONY: install lint test scan firewall dashboard

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

lint:
	. .venv/bin/activate && black scanner ai-firewall governance

test:
	. .venv/bin/activate && pytest -q

scan:
	. .venv/bin/activate && python scanner/cli.py --subscription-id $$AZ_SUBSCRIPTION_ID

firewall:
	. .venv/bin/activate && uvicorn ai-firewall.server:app --reload

dashboard:
	. .venv/bin/activate && streamlit run dashboard/real_time_monitoring.py
