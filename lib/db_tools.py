import sqlite3


def record_feature_id(group):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()

    script = f"INSERT INTO feature_ids VALUES ('{group.name}', 'cluster_{group.id}');"
    cur.execute(script)

    conn.commit()
    conn.close()
