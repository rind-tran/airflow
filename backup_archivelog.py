
from datetime import datetime, timedelta
from textwrap import dedent
import pendulum

# The DAG object;
from airflow import DAG

# SSHHooK for SSH connections
from airflow.providers.ssh.hooks.ssh import SSHHook
from airflow.providers.ssh.operators.ssh import SSHOperator

# Operators;
from airflow.operators.bash import BashOperator

# Webhook
from ms_teams_webhook_operator import MSTeamsWebhookOperator


# Functions
def on_failure(context):

    dag_id = context['dag_run'].dag_id

    task_id = context['task_instance'].task_id
    context['task_instance'].xcom_push(key=dag_id, value=True)

    logs_url = "https://vnhqmgrdb01.hcnet.vn:8080/log?dag_id={}&task_id={}&execution_date={}".format(
         dag_id, task_id, context['ts'])

    teams_notification = MSTeamsWebhookOperator(
        task_id="msteams_notify_failure", trigger_rule="all_done",
        message="**Airflow notification**: `{}` has failed on task: `{}`".format(dag_id, task_id),
        button_text="View log", button_url=logs_url,
        theme_color="FF0000", http_conn_id='msteams_webhook_url')
    teams_notification.execute(context)


# Define SSHHook
sshHook = SSHHook(ssh_conn_id="dbgenesys03_ssh")

# Define DAG
with DAG(
    "dbgenesys03_backup_archivelog",
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        "depends_on_past": False,
        "email": ["airflow@example.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "on_failure_callback": on_failure,
        # 'queue': 'bash_queue',
        # 'pool': 'backfill',
        # 'priority_weight': 10,
        # 'end_date': datetime(2016, 1, 1),
        # 'wait_for_downstream': False,
        # 'sla': timedelta(hours=2),
        # 'execution_timeout': timedelta(seconds=300),
        # 'on_failure_callback': some_function, # or list of functions
        # 'on_success_callback': some_other_function, # or list of functions
        # 'on_retry_callback': another_function, # or list of functions
        # 'sla_miss_callback': yet_another_function, # or list of functions
        # 'trigger_rule': 'all_success'
    },
    description="dbgenesys03 backup archivelog",
    start_date=pendulum.datetime(2023, 6, 14, tz="Asia/Saigon"),
    schedule_interval='30 12,21 * * *',
    catchup=False,
    tags=["dbgenesys03","genesys"],
) as dag:
    command_01="/home/oracle/bin/main_backup_archivelog.sh gsvn1 > /dev/null 2>&1 "


    # Tasks
    t1 = SSHOperator(
        task_id="backup_archivelog",
        command=command_01,
        ssh_hook=sshHook,
        cmd_timeout=None,
    )
