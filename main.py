import os
import ctypes
import subprocess
import platform
import tempfile
import psutil
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()


def is_admin():
    """Check if the script is running with Administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def get_size_format(b, factor=1024, suffix="B"):
    """Convert bytes into a human-readable format (MB, GB, etc.)."""
    for unit in ["", "K", "M", "G", "T"]:
        if b < factor:
            return f"{b:.2f} {unit}{suffix}"
        b /= factor
    return f"{b:.2f} P{suffix}"


def optimize_ram():
    """Trim process Working Sets using the native Windows PSAPI."""
    if platform.system().lower() != "windows":
        console.print("[red]This feature is only supported on Windows.[/red]")
        return

    mem_before = psutil.virtual_memory().used
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_SET_QUOTA = 0x0100
    cleaned_procs = 0

    with console.status("[bold cyan]Trimming standby RAM (Process Working Sets)..."):
        for proc in psutil.process_iter(["pid"]):
            pid = proc.info["pid"]
            if pid in (0, 4):
                continue
            try:
                handle = ctypes.windll.kernel32.OpenProcess(
                    PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA, False, pid
                )
                if handle:
                    res = ctypes.windll.psapi.EmptyWorkingSet(handle)
                    if res != 0:
                        cleaned_procs += 1
                    ctypes.windll.kernel32.CloseHandle(handle)
            except Exception:
                pass

    mem_after = psutil.virtual_memory().used
    freed_ram = max(0, mem_before - mem_after)

    console.print(
        Panel(
            f"[bold green]RAM Optimization Completed[/bold green]\n"
            f"Processes optimized: [bold]{cleaned_procs}[/bold]\n"
            f"Physical RAM recovered: [bold cyan]{get_size_format(freed_ram)}[/bold cyan]\n"
            f"Current RAM usage: [bold yellow]{psutil.virtual_memory().percent}%[/bold yellow]",
            title="Memory Optimizer (Windows API)",
            border_style="cyan",
        )
    )


def deep_clean():
    """Clean User Temp, Windows Temp, Prefetch, and GPU Shader Caches."""
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    win_dir = os.environ.get("WINDIR", "C:\\Windows")

    targets = [
        ("User Temp (%TEMP%)", tempfile.gettempdir()),
        ("Windows Temp", os.path.join(win_dir, "Temp")),
        ("Windows Prefetch", os.path.join(win_dir, "Prefetch")),
        ("DirectX Shader Cache", os.path.join(local_app_data, "D3DSCache")),
        ("NVIDIA DXCache", os.path.join(local_app_data, "NVIDIA", "DXCache")),
        ("AMD DxCache", os.path.join(local_app_data, "AMD", "DxCache")),
    ]

    table = Table(title="Deep Clean Results", header_style="bold green")
    table.add_column("Location / Cache", style="cyan")
    table.add_column("Files Removed", justify="right")
    table.add_column("Space Recovered", justify="right", style="bold green")

    total_freed = 0
    total_files = 0

    with console.status("[bold yellow]Cleaning system temp files and GPU shader cache..."):
        for label, folder in targets:
            if not folder or not os.path.exists(folder):
                continue

            folder_freed = 0
            folder_files = 0

            for root, dirs, files in os.walk(folder, topdown=False):
                for name in files:
                    file_path = os.path.join(root, name)
                    try:
                        size = os.path.getsize(file_path)
                        os.remove(file_path)
                        folder_freed += size
                        folder_files += 1
                    except Exception:
                        pass
                for name in dirs:
                    try:
                        os.rmdir(os.path.join(root, name))
                    except Exception:
                        pass

            total_freed += folder_freed
            total_files += folder_files
            table.add_row(label, str(folder_files), get_size_format(folder_freed))

    console.print(table)
    console.print(
        f"[bold green]Total Space Freed:[/bold green] {get_size_format(total_freed)} "
        f"({total_files} files deleted)."
    )


def gaming_mode_processes():
    """Display top RAM processes and kill background bloatware or specific PIDs."""
    bloatware_list = [
        "OneDrive.exe",
        "YourPhone.exe",
        "PhoneExperienceHost.exe",
        "Widgets.exe",
        "WidgetService.exe",
        "GameBarPresenceWriter.exe",
        "Cortana.exe",
        "Teams.exe",
    ]

    processes = []
    for proc in psutil.process_iter(["pid", "name", "memory_info"]):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    top_procs = sorted(
        processes,
        key=lambda p: p["memory_info"].rss if p["memory_info"] else 0,
        reverse=True,
    )[:8]

    table = Table(title="Top 8 Processes by RAM Usage", header_style="bold yellow")
    table.add_column("PID", style="cyan", width=8)
    table.add_column("Process Name", style="bold white", width=28)
    table.add_column("RAM Usage", justify="right", style="green")

    for p in top_procs:
        table.add_row(str(p["pid"]), p["name"], get_size_format(p["memory_info"].rss))

    console.print(table)
    console.print("\n[bold]Process Optimization Actions:[/bold]")
    console.print("1. Kill Windows Background Bloatware (Widgets, Phone Link, OneDrive, etc.)")
    console.print("2. Terminate a specific process by PID")
    console.print("3. Back to Main Menu")

    sub = Prompt.ask("Select action", choices=["1", "2", "3"], default="3")

    if sub == "1":
        killed = []
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if proc.info["name"] in bloatware_list:
                    proc.terminate()
                    killed.append(proc.info["name"])
            except Exception:
                pass
        if killed:
            console.print(f"[bold green]Terminated processes:[/bold green] {', '.join(set(killed))}")
        else:
            console.print("[dim]No target bloatware processes are currently running.[/dim]")

    elif sub == "2":
        pid_str = Prompt.ask("Enter the PID number to terminate")
        if pid_str.isdigit():
            try:
                p = psutil.Process(int(pid_str))
                name = p.name()
                if Confirm.ask(f"Are you sure you want to terminate [bold red]{name}[/bold red] (PID {pid_str})?"):
                    p.terminate()
                    console.print(f"[bold green]Process {name} terminated.[/bold green]")
            except Exception as e:
                console.print(f"[red]Failed to terminate process: {e}[/red]")


def optimize_network():
    """Flush DNS cache, tune TCP stack, and test latency to global nodes."""
    with console.status("[bold blue]Flushing DNS cache and optimizing TCP/IP stack..."):
        commands = [
            ["ipconfig", "/flushdns"],
            ["netsh", "int", "tcp", "set", "global", "autotuninglevel=normal"],
        ]
        for cmd in commands:
            try:
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

    console.print("[bold green]✔ DNS cache flushed and TCP Auto-Tuning set to normal.[/bold green]")

    targets = [
        ("Cloudflare Global DNS", "1.1.1.1"),
        ("Google Global DNS", "8.8.8.8"),
        ("AWS US-East (Virginia)", "ec2.us-east-1.amazonaws.com"),
        ("AWS Europe (Frankfurt)", "ec2.eu-central-1.amazonaws.com"),
        ("AWS South America (São Paulo)", "ec2.sa-east-1.amazonaws.com"),
    ]

    table = Table(title="Network Latency Benchmark", header_style="bold blue")
    table.add_column("Target Server", style="cyan")
    table.add_column("Host", style="dim")
    table.add_column("Latency", justify="right")

    with console.status("[bold green]Running ping benchmark..."):
        for name, host in targets:
            ms = ping_host(host)
            if ms is None:
                status = "[red]Timeout[/red]"
            elif ms < 45:
                status = f"[bold green]{ms:.0f} ms (Optimal)[/bold green]"
            elif ms < 110:
                status = f"[yellow]{ms:.0f} ms (Fair)[/yellow]"
            else:
                status = f"[red]{ms:.0f} ms (High)[/red]"
            table.add_row(name, host, status)

    console.print(table)


def ping_host(host):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        output = subprocess.check_output(
            ["ping", param, "2", host], stderr=subprocess.STDOUT, universal_newlines=True
        )
        for line in output.splitlines():
            if "time=" in line.lower() or "tiempo=" in line.lower():
                parts = line.replace("tiempo=", "time=").split("time=")[1]
                return float(parts.split("ms")[0].strip().replace("<", ""))
    except Exception:
        return None
    return None


def unlock_ultimate_power():
    """Unlock and activate Windows High/Ultimate Performance power plans."""
    console.print("\n[bold cyan]Windows Power Plan Manager:[/bold cyan]")
    console.print("1. Enable [bold yellow]High / Ultimate Performance[/bold yellow] (Best for Gaming & Desktops)")
    console.print("2. Enable [bold green]Balanced Mode[/bold green] (Recommended for Laptops on battery)")

    opt = Prompt.ask("Select power plan", choices=["1", "2"], default="1")

    try:
        if opt == "1":
            subprocess.run(
                ["powercfg", "-duplicatescheme", "e9a42b02-d5df-448d-aa00-03f14749eb61"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            subprocess.run(["powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], check=True)
            console.print("[bold green]✔ High/Ultimate Performance Power Plan activated.[/bold green]")
        else:
            subprocess.run(["powercfg", "/setactive", "381b4222-f694-41f0-9685-ff5bb260df2e"], check=True)
            console.print("[bold green]✔ Balanced Power Plan restored.[/bold green]")
    except Exception as e:
        console.print(f"[red]Failed to switch power plan (Run as Administrator): {e}[/red]")


def system_summary():
    """Display a quick overview of CPU, RAM, and Disk status."""
    cpu = psutil.cpu_percent(interval=0.7)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    table = Table(title="System Hardware Overview", header_style="bold magenta")
    table.add_column("Component", style="cyan")
    table.add_column("Usage", justify="right")
    table.add_column("Available / Free", justify="right", style="green")

    table.add_row("CPU", f"{cpu}%", f"{100 - cpu:.1f}% idle")
    table.add_row("RAM", f"{ram.percent}%", f"{get_size_format(ram.available)} available")
    table.add_row("Primary Disk", f"{disk.percent}%", f"{get_size_format(disk.free)} free")
    console.print(table)


def main():
    admin_badge = (
        "[bold green]ADMINISTRATOR MODE ACTIVE[/bold green]"
        if is_admin()
        else "[bold yellow]STANDARD MODE (Run via run.bat for full access)[/bold yellow]"
    )

    console.print(
        Panel.fit(
            f"[bold white]PC-PULSE v2.0[/bold white] - Windows Optimization & Diagnostics Suite\n"
            f"{admin_badge}",
            border_style="cyan",
        )
    )

    while True:
        console.print("\n[bold]Optimization Menu:[/bold]")
        console.print("1. [bold cyan]Optimize RAM[/bold cyan] (Trim Standby Working Set)")
        console.print("2. [bold green]Deep Clean[/bold green] (Windows Temp, Prefetch & GPU Shader Cache)")
        console.print("3. [bold yellow]Gaming Mode[/bold yellow] (Kill Background Bloatware or PIDs)")
        console.print("4. [bold blue]Network & DNS Boost[/bold blue] (Flush DNS + TCP Auto-Tuning + Ping Test)")
        console.print("5. [bold magenta]Unlock High/Ultimate Power Plan[/bold magenta]")
        console.print("6. Hardware Resource Summary (CPU / RAM / Disk)")
        console.print("7. Exit")

        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5", "6", "7"], default="1")

        if choice == "1":
            optimize_ram()
        elif choice == "2":
            deep_clean()
        elif choice == "3":
            gaming_mode_processes()
        elif choice == "4":
            optimize_network()
        elif choice == "5":
            unlock_ultimate_power()
        elif choice == "6":
            system_summary()
        elif choice == "7":
            console.print("[bold cyan]System optimized! Goodbye.[/bold cyan]")
            break


if __name__ == "__main__":
    main()