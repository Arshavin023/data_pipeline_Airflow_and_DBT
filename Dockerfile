FROM quay.io/astronomer/astro-runtime:10.2.0

RUN python -m venv soda_venv && source soda_venv/bin/activate && \
    pip install --no-cache-dir --default-timeout=100 setuptools==69.0.3 wheel==0.42.0 && \
    pip install --no-cache-dir --index-url=https://pypi.python.org/simple/ soda-core-bigquery==3.0.45 && \
    pip install --no-cache-dir --index-url=https://pypi.python.org/simple/ soda-core-scientific==3.0.45 && \
    deactivate


# RUN python -m venv soda_venv && source soda_venv/bin/activate && \
#     pip install --no-cache-dir --index-url=https://pypi.python.org/simple/ soda-core-bigquery==3.0.45 && \
#     pip install --no-cache-dir --index-url=https://pypi.python.org/simple/ soda-core-scientific==3.0.45 && \
#     deactivate

# RUN python -m venv soda_venv && source soda_venv/bin/activate && \
#     pip install --no-cache-dir soda-core-bigquery==3.0.45 && \
#     pip install --no-cache-dir soda-core-scientific==3.0.45 && deactivate

