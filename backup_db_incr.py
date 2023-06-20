
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
from airflow.operators.python import PythonOperator, BranchPythonOperator

# Dummy
from airflow.operators.empty import EmptyOperator


# Variables
tabDays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


# returns the week day (monday, tuesday, etc.)
def get_day(**kwargs):
    kwargs['ti'].xcom_push(key='day', value=datetime.now().weekday())

# check if today is from monday to saturday, returns the name id of the task to launch (backup_task, no_task, etc.)
def branch(**kwargs):
    today = tabDays[kwargs['ti'].xcom_pull(task_ids='weekday', key='day')]
    if today == 'sunday':
        return 'no_task'
    else:
        return 'backup_db_incr'

sshHook = SSHHook(ssh_conn_id="dbgenesys03_ssh")

with DAG(
    "dbgenesys03_backup_db_incr",
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        "depends_on_past": False,
        "email": ["airflow@example.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
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
    command_01="/home/oracle/bin/main_backup_database_incremental_level.sh gsvn1 inc > /dev/null 2>&1 "
   

    # Tasks
    # PythonOperator will retrieve and store into "weekday" variable the week day
    get_weekday = PythonOperator(
    task_id='weekday',
    python_callable=get_day,
    provide_context=True,
    dag=dag
    )

    # BranchPythonOperator will use "weekday" variable, and decide which task to launch next
    fork = BranchPythonOperator(
    task_id='branching',
    python_callable=branch,
    provide_context=True,
    dag=dag)

    backup = SSHOperator(
        task_id="backup_db_incr",
        command=command_01,
        ssh_hook=sshHook,
        cmd_timeout=None,
    )

    # task 1, get the week day
    get_weekday.set_downstream(fork)

    # Monday - Saturday: backup db incr, Sunday: do nothing 
    fork.set_downstream(backup)
    fork.set_downstream(EmptyOperator(task_id='no_task', dag=dag))
