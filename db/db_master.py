from db.connection import get_conn

def add_master(record):
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()

        query = """
            INSERT INTO cca_master (
                cca_id, property_id, from_mail, to_mail, cc_mail,
                subject, body, source_agent, notify_teams, status
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id;
        """

        cur.execute(query, (
            record.get("cca_id"),
            record.get("property_id"),
            record.get("from_mail"),
            record.get("to_mail"),
            record.get("cc_mail"),
            record.get("subject"),
            record.get("body"),
            record.get("source_agent"),
            record.get("notify_teams", False),
            record.get("status", "OPEN")
        ))

        new_id = cur.fetchone()[0]
        conn.commit()

        return {"status": "success", "id": new_id}

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        if conn:
            conn.close()


def get_last_cca_id(property_id: int):
    """Return last CCA ID for this property or None."""
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT cca_id 
        FROM cca_master 
        WHERE property_id = %s 
        ORDER BY id DESC 
        LIMIT 1
    """, (property_id,))

    row = cur.fetchone()
    cur.close()
    conn.close()

    return row[0] if row else None
