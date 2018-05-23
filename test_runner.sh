#!/bin/sh
echo 'Run tests\n'
echo $(python -m pytest tests/smoke_endpoint_test.py)
echo $(python -m pytest tests/data_provider_test.py)
echo $(python -m pytest tests/webhook_endpoint_test.py)
echo $(python -m pytest tests/db_endpoint_test.py)
echo $(python -m pytest tests/limit_endpoint_test.py)
echo 'Run Flake8'
echo $(flake8 --max-line-length=120)