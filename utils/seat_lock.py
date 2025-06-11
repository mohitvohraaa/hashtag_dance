from utils.redis import redis_client
from django.conf import settings

lock_duration=settings.REDIS_LOCK_DURATION
def are_seats_locked(event_id,seats):
    for seat in seats:
        lock_key=f"lock:{event_id}:{seat}"
        if redis_client.exists(lock_key):
            return True
    return False

def lock_seats(event_id,seats,user_id):
    for seat in seats:
        lock_key=f"lock:{event_id}:{seat}"
        redis_client.setex(lock_key,lock_duration,user_id)


def unlock_seats(event_id,seats):
    for seat in seats:
        redis_client.delete(f"lock:{event_id}:{seat}")
def fetch_locked_seats(event_id):
    locked_seats = []

    try:
        for key in redis_client.scan_iter(f"lock:{event_id}:*"):
            try:
                # Ensure key is string if decode_responses wasn't set
                if isinstance(key, bytes):
                    key = key.decode()

                seat_id = key.split(":")[-1]
                if seat_id:
                    locked_seats.append(seat_id)
            except Exception as inner_e:
                print(f"Key parsing error in fetch_locked_seats: {inner_e}")
                continue

    except Exception as e:
        print(f"Redis fetch error for event {event_id}: {e}")

    return locked_seats

