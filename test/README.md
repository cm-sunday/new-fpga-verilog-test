# Silicon Dreams - Tool Detection & Setup Script

<div align="center">

![Version](https://img.shields.io/badge/version-1.0-blue.svg)
![Bash](https://img.shields.io/badge/shell-bash-green.svg)
![License](https://img.shields.io/badge/license-Chipmango-orange.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)

**A comprehensive tool detection and setup script for FPGA/Verilog development environments**

*Presented by ChipMango x ChipFoudary*

</div>

---

##  Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [Command Line Options](#command-line-options)
- [Interactive Menu](#interactive-menu)
- [Supported Tools](#supported-tools)
- [Platform Support](#platform-support)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Logging & Reports](#logging--reports)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The Silicon Dreams Tool Detection & Setup Script is a powerful, user-friendly utility that automates the setup of FPGA/Verilog development environments. It scans your system for required tools, displays their versions, and optionally installs only the missing components **without overwriting** existing installations.

### Why Use This Script?

-  **No guesswork** - Automatically detects what's already installed
-  **Safe operations** - Never overwrites existing tools or configurations
-  **Cross-platform** - Works on Linux, macOS, and Windows
-  **Interactive & Automated** - Choose your preferred workflow
-  **Detailed reporting** - Generates comprehensive system reports
-  **Recovery friendly** - Saves state and provides cleanup options

---

## Features

### Core Capabilities
-  **Smart Detection** - Scans for 10+ development tools and packages
-  **Version Checking** - Shows detailed version information
-  **Selective Installation** - Installs ONLY missing components
-  **Cross-Platform** - Native support for all major OS
-  **Comprehensive Logging** - Everything logged for debugging
-  **Docker Support** - Optional containerized workflow

### Safety Features
-  **No Overwrites** - Preserves existing configurations
-  **State Saving** - Recovers from interrupted operations
-  **Dry Run Mode** - Preview changes before execution
-  **Verification** - Confirms installations worked
-  **Cleanup Options** - Remove failed installations

### User Experience
-  **Color Output** - Easy-to-read visual feedback
-  **Progress Indicators** - Spinners and progress bars
-  **Interactive Menu** - User-friendly interface
-  **Report Generation** - Shareable system reports
-  **Preferences** - Remembers your choices

---

## Prerequisites

### Required
- **Bash 4.0+** (or Git Bash on Windows)
- **Internet connection** (for installations)
- **Sudo/Admin access** (for system package installation)

### Optional but Recommended
- **Git** (for repository cloning)
- **Python 3.7+** (for cocotb tests)
- **Docker** (for containerized workflow)

---

## Quick Start

### One-liner to get started:

```bash
# Download and run the script
curl -O https://raw.githubusercontent.com/ChipMango/silicon-dreams/main/setup.sh
chmod +x setup.sh
./setup.sh
