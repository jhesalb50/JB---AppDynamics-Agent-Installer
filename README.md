---

# AppDynamics Agent Manager (Linux)

---

A secure, GUI‑based lifecycle manager for AppDynamics Machine Agents on Linux.  
Built for operators, SREs, and platform teams.

AppDynamics Agent Manager** provides a clean desktop interface for discovering, installing, configuring, and removing AppDynamics Machine Agents — without manual XML editing or shell‑only workflows.

---

## What It Does

- Detects existing AppDynamics Machine Agent installations
- Installs or uninstalls agents safely with backup support
- Generates and manages `controller-info.xml`
- Starts agents directly or via service discovery
- Displays agent status, version, and service state
- Logs all actions with timestamped activity tracking

---

## Enterprise‑Ready by Design

### ✅ Safe & Reversible
- Automatic backup of existing agent installations
- Non‑destructive uninstall workflow
- Explicit user‑initiated actions only

### ✅ Local‑First & Secure
- Runs entirely on the local system
- No telemetry, no cloud dependency
- Credentials are written only to local config files

### ✅ Operator‑Friendly
- GUI replaces error‑prone shell commands
- Real‑time activity logs
- Clear separation of discovery, install, and uninstall

---

## Core Capabilities

- Controller configuration (host, port, account, access key, application)
- Optional server visibility and HTTP listener toggles
- Agent package download and extraction
- Automatic permission handling
- Service state detection (`systemd`)
- Visual confirmation of configuration and runtime status

---

## Ideal Use Cases

- Linux server onboarding and observability rollout
- Lab, staging, and ephemeral environments
- Platform engineering and SRE workflows
- Air‑gapped or restricted enterprise networks
- Operators who prefer GUI over CLI‑only tooling

---

## Technology

- Python 3
- Tkinter GUI
- Native Linux utilities (`wget`, `tar`, `systemctl`)
- XML configuration management
- Threaded execution for non‑blocking UI

---

## Operating Model

- Designed for Linux systems with AppDynamics Machine Agent support
- Requires appropriate sudo privileges for install/uninstall actions
- Intended for controlled administrative environments

---

**AppDynamics Agent Manager**  
*Operational clarity for AppDynamics on Linux.*

---
