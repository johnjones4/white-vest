import random
import time

from whitevest.lib.buffer_session_store import BufferSessionStore


def test_buffer_session_store():
    store = BufferSessionStore("data", f"test_sessionstore_{time.time()}.sql")
    store.initialize()
    first_session = store.current_session.get_value()
    assert first_session >= int(time.time())
    store.buffer.append(random.random())
    time.sleep(1)
    store.create_new_session()
    next_session = store.current_session.get_value()
    assert next_session >= int(time.time())
    assert next_session != first_session
    assert store.buffer.size() == 0
    time.sleep(1)
    store.create_new_session()
    sessions = store.get_sessions()
    assert sessions == [next_session, first_session]
