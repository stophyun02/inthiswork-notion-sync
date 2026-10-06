from pathlib import Path


def test_bootstrap_pipeline_propagates_python_failure_and_captures_stderr():
    workflow = Path(".github/workflows/bootstrap.yml").read_text(encoding="utf-8")

    assert "set -o pipefail" in workflow
    assert "python -u -m src.bootstrap 2>&1 | tee bootstrap-output.txt" in workflow
    assert "bootstrap_status=${PIPESTATUS[0]}" in workflow
    assert 'exit "$bootstrap_status"' in workflow


def test_daily_schedule_is_0910_kst_in_utc():
    workflow = Path(".github/workflows/daily-sync.yml").read_text(encoding="utf-8")

    assert 'cron: "10 0 * * *"' in workflow
    assert 'timezone: "Asia/Seoul"' not in workflow


def test_sync_shell_keeps_failure_and_summary_in_both_modes(tmp_path):
    import os
    import subprocess
    import textwrap

    workflow = Path(".github/workflows/daily-sync.yml").read_text(encoding="utf-8")
    script = textwrap.dedent(workflow.split("        run: |\n")[-1])
    # Execute the actual workflow shell under GitHub's bash -e semantics.
    stub = tmp_path / "python"
    stub.write_text('#!/bin/bash\necho "module=$3"\necho diagnostic >&2\nexit "$STUB_EXIT"\n')
    stub.chmod(0o755)
    for check_only, module in [("true", "src.check_notion"), ("false", "src.sync")]:
        for status in [0, 7]:
            summary = tmp_path / f"summary-{check_only}-{status}"
            env = dict(os.environ, PATH=f"{tmp_path}:{os.environ['PATH']}",
                       GITHUB_STEP_SUMMARY=str(summary), CHECK_NOTION_ONLY=check_only,
                       STUB_EXIT=str(status))
            result = subprocess.run(["bash", "-e", "-c", script], cwd=tmp_path,
                                    env=env, capture_output=True, text=True)
            assert result.returncode == status, result.stderr
            assert f"module={module}" in summary.read_text()
            assert "diagnostic" in summary.read_text()
