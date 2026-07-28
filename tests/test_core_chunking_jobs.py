from __future__ import annotations

import json

import pytest

from sao_francisco.core import (
    BoundaryKind,
    ChunkSpec,
    JobStatus,
    JobStore,
    Segment,
    Transcript,
    plan_chunks,
)


def test_chunk_planner_prefers_silence_and_does_not_overlap_it() -> None:
    chunks = plan_chunks(
        130,
        silences=[(58, 60)],
        target_duration=60,
        search_window=5,
        overlap=3,
        min_duration=15,
    )

    assert len(chunks) == 2
    assert chunks[0].end == 59
    assert chunks[0].boundary == BoundaryKind.SILENCE
    assert chunks[1].start == 59
    assert chunks[1].overlap_before == 0
    assert chunks[-1].end == 130


def test_chunk_planner_adds_overlap_for_hard_cut() -> None:
    chunks = plan_chunks(
        125,
        target_duration=60,
        search_window=5,
        overlap=2,
        min_duration=10,
    )

    assert chunks[0].boundary == BoundaryKind.HARD
    assert chunks[0].end == 60
    assert chunks[1].start == 58
    assert chunks[1].overlap_before == 2


def test_job_store_resumes_from_individual_chunk_results(tmp_path) -> None:
    store = JobStore(tmp_path / "jobs")
    chunks = (ChunkSpec(0, 0, 10), ChunkSpec(1, 10, 20))
    job = store.create_job(
        job_id="job-1",
        source="/media/example.mp4",
        chunks=chunks,
        provider="openai",
        model="gpt-4o-mini-transcribe",
        language="pt",
    )
    transcript = Transcript(
        segments=(Segment(0, 5, "primeira parte"),),
        language="pt",
        duration=10,
    )

    updated = store.save_chunk_result(job.job_id, 0, transcript)

    assert updated.status == JobStatus.RUNNING
    assert updated.progress == 0.5
    assert [chunk.index for chunk in store.pending_chunks(job.job_id)] == [1]
    assert store.load_chunk_result(job.job_id, 0) == transcript
    assert not list(store.job_directory(job.job_id).glob(".manifest.json.*.tmp"))

    completed = store.save_chunk_result(job.job_id, 1, Transcript(duration=10))
    # The last transcription result is a checkpoint; only final export
    # completes the whole job.
    assert completed.status == JobStatus.RUNNING
    assert completed.progress == 1


def test_job_store_reconciles_result_written_before_manifest(tmp_path) -> None:
    store = JobStore(tmp_path / "jobs")
    job = store.create_job(
        job_id="interrupted",
        source="video.mp4",
        chunks=(ChunkSpec(0, 0, 10),),
        provider="gemini",
        model="gemini-test",
    )
    result = Transcript(
        segments=(Segment(0, 1, "salvo antes da queda"),),
        duration=10,
    )
    result_path = store.chunk_result_path(job.job_id, 0)
    result_path.write_text(
        json.dumps(result.to_dict(), ensure_ascii=False),
        encoding="utf-8",
    )

    resumed = store.resume_job(job.job_id)

    assert resumed.completed_chunks == frozenset({0})
    assert resumed.status == JobStatus.RUNNING


def test_job_store_rejects_path_traversal(tmp_path) -> None:
    store = JobStore(tmp_path / "jobs")
    with pytest.raises(ValueError):
        store.job_directory("../fora")
