import os
import threading

from distribution.gov_simulator import build_from_env


_started = False
_lock = threading.Lock()


def _is_enabled() -> bool:
    value = os.getenv('RUN_GOV_SIMULATOR_IN_WEB', 'false').strip().lower()
    return value in {'1', 'true', 'yes', 'on'}


def _run_simulator_forever():
    simulator = build_from_env()
    simulator.run_forever()


def start_embedded_simulator_if_enabled() -> bool:
    global _started

    if not _is_enabled():
        return False

    with _lock:
        if _started:
            return False

        thread = threading.Thread(
            target=_run_simulator_forever,
            name='gov-grid-simulator',
            daemon=True,
        )
        thread.start()
        _started = True
        return True
