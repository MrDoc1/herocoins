from config import host, database, user, password, port
import psycopg2
import datetime
import json


execute = False


def connect():
    conn = None
    try:
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port)
        cursor = conn.cursor()
        return conn, cursor
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def make_challenge_table() -> None:
    command = """
        CREATE TABLE challenges (
            name TEXT PRIMARY KEY,
            info JSON NOT NULL,
            modified TIMESTAMPTZ
        )
        """
    db, cursor = connect()
    cursor.execute(command)
    cursor.close()
    db.commit()
    db.close()
    print("Created table challenges.")
    return


def make_completed_table() -> None:
    command = "CREATE TABLE completed_challenges(user_id BIGINT,challenge_name TEXT REFERENCES challenges(name),completed_on TIMESTAMPTZ)"
    db, cursor = connect()
    cursor.execute(command)
    cursor.close()
    db.commit()
    db.close()
    print("Created table completed_challenges.")
    return


def make_current_challenge_table() -> None:
    command = "CREATE TABLE current_challenge(user_id BIGINT PRIMARY KEY,challenge_name TEXT REFERENCES challenges(name),timestamp TIMESTAMPTZ)"
    db, cursor = connect()
    cursor.execute(command)
    cursor.close()
    db.commit()
    db.close()
    print("Created table current_challenge.")
    return


if __name__ == "__main__":
    command = "INSERT INTO challenges VALUES (%s,%s,%s)"
    db, cursor = connect()
    cursor.execute(command,("None",json.dumps({}),datetime.datetime.utcnow()))
    cursor.close()
    db.commit()
    db.close()
    if execute:
        make_challenge_table()
        make_completed_table()
        make_current_challenge_table()