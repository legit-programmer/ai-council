from services.redis import RedisStore


store = RedisStore()
def add_message_from_console(session_id: str):
    msg = input("Enter your message: ")
    store.add_user_message(session_id, msg)

# while True:
#     add_message_from_console("session_123")

store.stop_session(session_id="session_123")