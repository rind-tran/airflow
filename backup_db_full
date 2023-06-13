
from datetime import datetime, timedelta
from textwrap import dedent

# The DAG object;
from airflow import DAG

# SSHHooK for SSH connections
from airflow.providers.ssh.hooks.ssh import SSHHook
from airflow.providers.ssh.operators.ssh import SSHOperator

# Operators;
from airflow.operators.bash import BashOperator

sshHook = SSHHook(ssh_conn_id="dbgenesys03_ssh")

with DAG(
    "dbgenesys03_backup_db_full",
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
    description="dbgenesys03 backup db full",
    start_date=datetime(2021, 1, 1),
    schedule_interval='30 23 * * 0',
    catchup=False,
    tags=["example"],
) as dag:
    command_01="/home/oracle/bin/main_backup_database_incremental_level.sh gsvn1 full > /dev/null 2>&1 "


    # t1, t2 and t3 are examples of tasks created by instantiating operators
    t1 = SSHOperator(
        task_id="backup_db_full",
        command=command_01,
        ssh_hook=sshHook,
    )

   


    # t1 >> t2 >> t3
