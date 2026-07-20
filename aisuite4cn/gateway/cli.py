"""Gateway server management - start/stop/restart with uvicorn."""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import click


PID_FILE = Path.home() / ".aisuite4cn" / "gateway.pid"
LOG_FILE = Path.home() / ".aisuite4cn" / "gateway.log"


def _ensure_dir():
    """Ensure the config directory exists."""
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)


def _read_pid() -> Optional[int]:
    """Read PID from file."""
    if PID_FILE.exists():
        try:
            return int(PID_FILE.read_text().strip())
        except (ValueError, OSError):
            return None
    return None


def _write_pid(pid: int):
    """Write PID to file."""
    _ensure_dir()
    PID_FILE.write_text(str(pid))


def _remove_pid():
    """Remove PID file."""
    if PID_FILE.exists():
        PID_FILE.unlink()


def _is_running(pid: int) -> bool:
    """Check if a process with given PID is running."""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


@click.group()
def cli():
    """aisuite4cn unified LLM access tool."""
    pass


@cli.group()
def gateway():
    """Manage the aisuite4cn HTTP gateway server."""
    pass


@gateway.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to.")
@click.option("--port", default=8000, type=int, help="Port to bind to.")
@click.option("--reload", is_flag=True, help="Enable auto-reload (dev only).")
@click.option("--config", "-c", default=None, help="Path to config file (.yaml or .json).")
@click.option(
    "--provider", "-p", multiple=True,
    help="Provider to pre-initialize (e.g., -p deepseek -p qwen)."
)
def start(host: str, port: int, reload: bool, config: Optional[str], provider: tuple):
    """Start the gateway server in the background."""
    existing_pid = _read_pid()
    if existing_pid and _is_running(existing_pid):
        click.echo(f"Gateway is already running (PID {existing_pid}).")
        sys.exit(1)

    _ensure_dir()

    cmd = [
        sys.executable, "-m", "aisuite4cn.gateway",
        "--host", host,
        "--port", str(port),
    ]
    if reload:
        cmd.append("--reload")
    if config:
        cmd.extend(["--config", config])

    log_fd = open(LOG_FILE, "a")
    process = subprocess.Popen(
        cmd,
        stdout=log_fd,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    _write_pid(process.pid)
    click.echo(f"Gateway started (PID {process.pid}) on {host}:{port}")
    if config:
        click.echo(f"Config file: {config}")
    click.echo(f"Log file: {LOG_FILE}")


@gateway.command()
def stop():
    """Stop the gateway server."""
    pid = _read_pid()
    if not pid:
        click.echo("No gateway PID file found. Is the gateway running?")
        sys.exit(1)

    if not _is_running(pid):
        click.echo(f"Gateway (PID {pid}) is not running. Cleaning up PID file.")
        _remove_pid()
        sys.exit(0)

    try:
        os.kill(pid, signal.SIGTERM)
        for _ in range(30):
            if not _is_running(pid):
                break
            time.sleep(0.5)
        else:
            os.kill(pid, signal.SIGKILL)
            time.sleep(0.5)
    except OSError:
        pass

    _remove_pid()
    click.echo(f"Gateway stopped (PID {pid}).")


@gateway.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to.")
@click.option("--port", default=8000, type=int, help="Port to bind to.")
@click.option("--reload", is_flag=True, help="Enable auto-reload (dev only).")
@click.option("--config", "-c", default=None, help="Path to config file (.yaml or .json).")
@click.option(
    "--provider", "-p", multiple=True,
    help="Provider to pre-initialize (e.g., -p deepseek -p qwen)."
)
def restart(host: str, port: int, reload: bool, config: Optional[str], provider: tuple):
    """Restart the gateway server."""
    pid = _read_pid()
    if pid and _is_running(pid):
        try:
            os.kill(pid, signal.SIGTERM)
            for _ in range(30):
                if not _is_running(pid):
                    break
                time.sleep(0.5)
            else:
                os.kill(pid, signal.SIGKILL)
                time.sleep(0.5)
        except OSError:
            pass
        _remove_pid()
        click.echo(f"Stopped gateway (PID {pid}).")
    else:
        click.echo("Gateway is not running. Starting...")

    _ensure_dir()

    cmd = [
        sys.executable, "-m", "aisuite4cn.gateway",
        "--host", host,
        "--port", str(port),
    ]
    if reload:
        cmd.append("--reload")
    if config:
        cmd.extend(["--config", config])

    log_fd = open(LOG_FILE, "a")
    process = subprocess.Popen(
        cmd,
        stdout=log_fd,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    _write_pid(process.pid)
    click.echo(f"Gateway restarted (PID {process.pid}) on {host}:{port}")
    if config:
        click.echo(f"Config file: {config}")
    click.echo(f"Log file: {LOG_FILE}")


def main():
    """Entry point for the gateway CLI."""
    cli()
