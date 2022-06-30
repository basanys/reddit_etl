import boto3
import configparser
import pathlib
import sys
from psycopg2 import sql
import psycopg2

parser = configparser.ConfigParser()
script_path = pathlib.Path(__file__).parent.resolve()
parser.read(f"{script_path}/configuration.conf")

USERNAME = parser.get("aws_config", "redshift_username")
PASSWORD = parser.get("aws_config", "redshift_password")
HOST = parser.get("aws_config", "redshift_hostname")
PORT = parser.get("aws_config", "redshift_port")
REDSHIFT_ROLE = parser.get("aws_config", "redshift_role")
DATABASE = parser.get("aws_config", "redshift_database")
BUCKET_NAME = parser.get("aws_config", "bucket_name")
ACCOUNT_ID = parser.get("aws_config", "account_id")
TABLE_NAME = 'reddit'

output_name = sys.argv[1]

file_path = f"s3://{BUCKET_NAME}/{output_name}.csv"

role_string = f'arn:aws:iam::{ACCOUNT_ID}:role/{REDSHIFT_ROLE}'

sql_create_table = sql.SQL("""CREATE TABLE IF NOT EXISTS {table} (
                            id varchar PRIMARY KEY,
                            title varchar(max),
                            num_comments int,
                            score int,
                            author varchar(max),
                            created_utc varchar(max),
                            url varchar(max),
                            upvote_ratio float,
                            over_18 bool,
                            
                            spoiler bool,
                            stickied bool
                        );""").format(table = sql.Identifier(TABLE_NAME))

# If ID already exists in table, we remove it and add new ID record during load.
create_temp_table = sql.SQL("CREATE TEMP TABLE our_staging_table (LIKE {table});").format(table = sql.Identifier(TABLE_NAME))
sql_copy_to_temp = f"COPY our_staging_table FROM '{file_path}' iam_role '{role_string}' IGNOREHEADER 1 DELIMITER ',' CSV;"
delete_from_table = sql.SQL("DELETE FROM {table} USING our_staging_table WHERE {table}.id = our_staging_table.id;").format(table = sql.Identifier(TABLE_NAME))
insert_into_table = sql.SQL("INSERT INTO {table} SELECT * FROM our_staging_table;").format(table = sql.Identifier(TABLE_NAME))
drop_temp_table = "DROP TABLE our_staging_table;"


def main():
    conn = connect_to_redshift()
    load_to_redshift(conn)



def connect_to_redshift():
    rs_conn = psycopg2.connect(dbname = DATABASE, user = USERNAME, password = PASSWORD, host = HOST, port = PORT)
    return rs_conn

def load_to_redshift(conn):

    cur = conn.cursor()

    cur.execute(sql_create_table)
    cur.execute(create_temp_table)
    cur.execute(sql_copy_to_temp)
    cur.execute(delete_from_table)
    cur.execute(insert_into_table)
    cur.execute(drop_temp_table)

    conn.commit()


if __name__ == "__main__":
    main()