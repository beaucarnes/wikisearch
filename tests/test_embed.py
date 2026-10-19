"""Connection recovery tests; these do not download the model or use the network."""
import unittest
from unittest.mock import MagicMock, patch
import psycopg
from embed import Database, save_batch


def connection():
    conn = MagicMock()
    conn.closed = False
    return conn


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.connect = patch('embed.psycopg.connect').start()
        self.register = patch('embed.register_vector').start()
        self.sleep = patch('embed.time.sleep').start()
        patch('embed.database_url', return_value='postgresql://test.invalid/test').start()
        patch('builtins.print').start()
        self.addCleanup(patch.stopall)

    def test_read_failure_reconnects_and_registers_vector_again(self):
        first, second = connection(), connection()
        self.connect.side_effect = [first, second]
        first.execute.side_effect = psycopg.OperationalError('connection lost')
        second.execute.return_value.fetchone.return_value = (42,)
        db = Database()
        try:
            result = db.run(lambda c: c.execute('SELECT 42').fetchone(), 'reading')
            self.assertEqual(result, (42,))
            first.close.assert_called_once()
            self.assertEqual(self.register.call_count, 2)
            self.sleep.assert_called_once_with(2)
        finally:
            db.close()

    def test_initial_connection_failure_is_retried(self):
        self.connect.side_effect = [psycopg.OperationalError('TLS failed'), connection()]
        db = Database()
        try:
            self.assertEqual(db.run(lambda c: 'connected', 'connecting'), 'connected')
            self.assertEqual(self.connect.call_count, 2)
        finally:
            db.close()

    def test_repeated_failures_are_bounded(self):
        self.connect.side_effect = psycopg.OperationalError('offline')
        db = Database(attempts=3)
        with self.assertRaises(psycopg.OperationalError):
            db.run(lambda c: None, 'connecting')
        self.assertEqual(self.connect.call_count, 3)
        self.assertEqual(self.sleep.call_count, 2)

    def test_query_cancellation_is_not_treated_as_a_connection_failure(self):
        conn = connection()
        self.connect.return_value = conn
        conn.execute.side_effect = psycopg.errors.QueryCanceled('cancelled')
        db = Database()
        with self.assertRaises(psycopg.errors.QueryCanceled):
            db.run(lambda c: c.execute('SELECT 1'), 'reading')
        self.connect.assert_called_once()
        self.sleep.assert_not_called()

    def test_lost_commit_response_replays_whole_batch_with_null_guard(self):
        first, second = connection(), connection()
        self.connect.side_effect = [first, second]
        # The server may commit successfully and then lose the COMMIT response.
        # Retrying must retain the exact vectors and the WHERE embedding IS NULL guard.
        first.transaction.return_value.__exit__.side_effect = psycopg.OperationalError(
            'lost COMMIT response'
        )
        updates = [([0.1, 0.2], 123), ([0.3, 0.4], 456)]
        db = Database()
        try:
            db.run(lambda c: save_batch(c, updates), 'saving')
            for conn in (first, second):
                cur = conn.cursor.return_value.__enter__.return_value
                cur.executemany.assert_called_once_with(
                    'UPDATE articles SET embedding=%s WHERE id=%s AND embedding IS NULL',
                    updates,
                )
                conn.transaction.assert_called_once()
            first.close.assert_called_once()
        finally:
            db.close()


if __name__ == '__main__':
    unittest.main()
