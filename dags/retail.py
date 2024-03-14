from airflow.decorators import dag, task
from airflow import AirflowException
from datetime import datetime
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyDatasetOperator
from astro import sql as aql  # best for transferring files to data transformation system
from astro.files import File
from astro.sql import Table, Metadata
from astro.constants import FileType
from include.dbt.cosmos_config import DBT_CONFIG, DBT_PROJECT_CONFIG
from cosmos.airflow.task_group import DbtTaskGroup
from cosmos.constants import LoadMode
from cosmos.config import RenderConfig
from airflow.models.baseoperator import chain

@dag(
    start_date=datetime(2024, 2, 29),
    schedule='0 1 * * *',
    catchup=False,
    tags=['retail'],
)
def retail():
    @task
    def check_upload_csv_to_gcs():
        # Check if upload_csv_to_gcs task was successful
        if not upload_csv_to_gcs.task_instance:
            raise AirflowException("Failed to upload CSV file to GCS")

    @task
    def check_create_retail_dataset():
        # Check if create_retail_dataset task was successful
        if not create_retail_dataset.task_instance:
            raise AirflowException("Failed to create retail dataset")

    @task
    def check_gcs_to_raw():
        # Check if gcs_to_raw task was successful
        if not gcs_to_raw.task_instance:
            raise AirflowException("Failed to load file from GCS to raw table")

    @task
    def check_load():
        # Check if check_load task was successful
        if not check_load.task_instance:
            raise AirflowException("Failed to check load")

    @task
    def check_transform():
        # Check if transform task was successful
        if not transform.task_instance:
            raise AirflowException("Failed to transform data")

    @task
    def check_report():
        # Check if report task was successful
        if not report.task_instance:
            raise AirflowException("Failed to generate report")

    upload_csv_to_gcs = LocalFilesystemToGCSOperator(
        task_id='upload_csv_to_gcs',
        src='/usr/local/airflow/include/dataset/online_retail.csv',
        dst='raw/online_retail.csv',
        bucket='analytics_engineer_learning',
        gcp_conn_id='gcp',
        mime_type='text/csv',
    )

    create_retail_dataset = BigQueryCreateEmptyDatasetOperator(
        task_id='create_retail_dataset',
        dataset_id='retail',
        gcp_conn_id='gcp',
    )

    gcs_to_raw = aql.load_file(
        task_id='gcs_to_raw',
        input_file=File(
            'gs://analytics_bucket/raw/online_retail.csv',
            conn_id='gcp',
            filetype=FileType.CSV,
        ),
        output_table=Table(
            name='raw_invoices',
            conn_id='gcp',
            metadata=Metadata(schema='retail')
        ),
        use_native_support=False,
    )

    transform = DbtTaskGroup(
        group_id='transform',
        project_config=DBT_PROJECT_CONFIG,
        profile_config=DBT_CONFIG,
        render_config=RenderConfig(
            load_method=LoadMode.DBT_LS,
            select=['path:models/transform']
        ))

    report = DbtTaskGroup(
        group_id='report',
        project_config=DBT_PROJECT_CONFIG,
        profile_config=DBT_CONFIG,
        render_config=RenderConfig(
            load_method=LoadMode.DBT_LS,
            select=['path:models/report'])
    )

    chain(
        upload_csv_to_gcs,
        check_upload_csv_to_gcs(),
        create_retail_dataset,
        check_create_retail_dataset(),
        gcs_to_raw,
        check_gcs_to_raw(),
        check_load(),
        transform,
        check_transform(),
        report,
        check_report(),
    )

dag = retail()