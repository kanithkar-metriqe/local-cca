from db.connection import get_conn

def add_thread(record):
    print("----------------------", record)
    try:
        conn = get_conn()
        cur = conn.cursor()

        query = """
            INSERT INTO cca_thread (
                cca_id, direction, from_mail, to_mail, cc_mail, subject, body,
                send_date, receive_date, attachments, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """

        cur.execute(query, (
            record.get("cca_id"),
            record.get("direction"),
            record.get("from_mail"),
            record.get("to_mail"),
            record.get("cc_mail"),
            record.get("subject"),
            record.get("body"),
            record.get("send_date"),
            record.get("receive_date"),
            record.get("attachments"),
            record.get("status"),
        ))

        new_id = cur.fetchone()[0]
        conn.commit()
        return {"status": "success", "id": new_id}

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        if conn:
            conn.close()
