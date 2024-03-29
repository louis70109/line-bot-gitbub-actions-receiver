import sqlite3
import logging

logger = logging.getLogger(__file__)


def connect():
    conn = sqlite3.connect("monitor.db")
    conn.row_factory = sqlite3.Row
    logger.info('Cursor init...')
    return conn


def exec(conn, stmt, args=None, fetch=True, commit=True):
    cursor = conn.cursor()
    try:
        if args:
            cursor.execute(stmt, args)
        else:
            cursor.execute(stmt)
        if commit:
            conn.commit()
        return [dict(row) for row in cursor.fetchall()] if fetch else None
    except:
        logger.exception("Error executing stmt: %s. args: %s", stmt, args)
        if commit:
            conn.rollback()
        raise


def exec_one(conn, stmt, args=None, fetch=True, commit=True):
    cursor = conn.cursor()
    try:
        if args:
            cursor.execute(stmt, args)
        else:
            cursor.execute(stmt)
        if commit:
            conn.commit()
        cur = cursor.fetchone()
        if cur is None:
            return None
        
        return dict(cur)
    except:
        logger.exception("Error executing stmt: %s. args: %s", stmt, args)
        if commit:
            conn.rollback()
        raise


def insert(conn, stmt, args=None, commit=True):
    cursor = conn.cursor()
    try:
        if args:
            cursor.execute(stmt, args)
        else:
            cursor.execute(stmt)
        if commit:
            conn.commit()
        return cursor.lastrowid
    except:
        logger.exception("Error executing stmt: %s. args: %s", stmt, args)
        if commit:
            conn.rollback()
        raise