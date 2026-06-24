# Transactional outbox

Commit business records and publishable events in one SQLite transaction.

Educational implementation with synthetic examples.

## Run

Python 3.9 or newer; standard library only. From this directory:

```sh
python3 main.py
python3 main.py --help
python3 -m unittest -v
```

The default example uses synthetic data and needs no credentials, installation, or network connection. The script also works by absolute path from another working directory.

## Behavior

Order creation atomically inserts an order and its outbox event. The publisher visits unsent events in insertion order and marks each sent only after the supplied callback succeeds. Reusing an order ID is rejected without creating another event.

## Use in Python

```python
from main import connect, create_order, publish_pending

db = connect()  # in-memory for this example
try:
    create_order(db, 'example-order', {'quantity': 1})
    published = publish_pending(db, lambda event_id, body: print(event_id, body))
finally:
    db.close()
```

## Design limits

The publication callback and database acknowledgment cannot be atomic together. Delivery is at least once: consumers must deduplicate event IDs. This demonstration uses one publisher, trusted callbacks, and a local SQLite connection; it provides no worker locking or network transport.

## Verification

The unit tests cover successful operations, failure paths, and invariants. These are local correctness checks, not production performance or security certification.

## Repository checks

```sh
python3 verify.py
```

This runs the isolated test suite, synthetic example, and CLI help. The included GitHub Actions workflow repeats these checks when the repository is published. No hosted CI result is claimed by the local verification report.
