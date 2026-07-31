from __future__ import annotations

from sao_francisco.process_smoke import run_process_smoke_test


def test_process_smoke_starts_forces_stop_and_reuses_spawn_boundary() -> None:
    assert run_process_smoke_test() == 0
