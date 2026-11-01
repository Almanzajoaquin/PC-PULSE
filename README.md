# ⚡ PC-Pulse v2.0 — Windows Optimization & Gaming Suite

![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6?style=for-the-badge&logo=windows)
![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Downloads](https://img.shields.io/github/downloads/Almanzajoaquin/PC-PULSE/total?style=for-the-badge&color=2ea44f)
![Stars](https://img.shields.io/github/stars/Almanzajoaquin/PC-PULSE?style=for-the-badge&color=yellow)

**PC-Pulse** is a lightweight, open-source CLI utility designed to free up standby memory, clean GPU shader caches, reduce network latency, and eliminate Windows background bloatware in seconds.

## 🚀 Key Features

- **🧠 Native RAM Optimizer:** Uses the Windows PSAPI (`EmptyWorkingSet`) to safely trim standby memory from background processes without crashing active apps.
- **🧹 Deep System & GPU Cleaner:** Wipes `%TEMP%`, `Windows\Temp`, `Prefetch`, and **DirectX / NVIDIA / AMD Shader Caches** to fix gaming micro-stuttering.
- **🎮 Gaming Mode (Bloatware Killer):** Instantly terminates resource-heavy background tasks (`Widgets`, `Phone Link`, `OneDrive`, `GameBar`) or any custom PID.
- **🌐 Network & DNS Boost:** Flushes DNS cache, resets TCP Auto-Tuning, and benchmarks latency against global DNS and AWS regional servers.
- **⚡ Ultimate Performance Unlocker:** Unlocks and activates Windows' hidden *Ultimate Performance* power scheme with a single keypress.

## 📦 Installation & Usage

### Option A: Standalone Executable (No Python Required)
1. Go to the **[Latest Release](https://github.com/Almanzajoaquin/PC-PULSE/releases/latest)** page.
2. Download **`pc-pulse.exe`**.
3. Run it (automatically requests Administrator privileges for deep system cleaning).

### Option B: Run from Source (Python)
1. Clone this repository:
```bash
git clone [https://github.com/Almanzajoaquin/PC-PULSE.git](https://github.com/Almanzajoaquin/PC-PULSE.git)
cd PC-PULSE
