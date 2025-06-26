# Apktool MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![Gemini CLI](https://img.shields.io/badge/Gemini-CLI-orange.svg)](https://github.com/google-gemini/gemini-cli)

A powerful **Model Context Protocol (MCP) server** that exposes [Apktool](https://ibotpeaches.github.io/Apktool/) functionality for Android APK analysis and reverse engineering. Integrates seamlessly with **Gemini CLI** to provide AI-powered APK security analysis, privacy auditing, and reverse engineering guidance through natural language commands.

## 🚀 Features

### 🔍 **Comprehensive APK Analysis**
- **Decompile APKs** to extract resources, manifest, and smali code
- **Analyze permissions** and app components for security assessment
- **Extract string resources** and detect hardcoded secrets
- **Search smali code** for specific patterns and security vulnerabilities
- **Recompile modified APKs** after making changes

### 🤖 **AI-Powered Workflows**
- **Natural language commands** for complex APK analysis tasks
- **Automated security audits** with AI-generated insights
- **Privacy compliance checking** and GDPR/CCPA analysis
- **Step-by-step reverse engineering** guidance
- **Intelligent vulnerability detection** and risk assessment

### 🛠 **8 Core Tools**
| Tool | Description |
|------|-------------|
| `decode_apk` | Decompile APK files to extract all components |
| `build_apk` | Recompile APK from modified source directory |
| `install_framework` | Install system frameworks for system app analysis |
| `analyze_manifest` | Parse AndroidManifest.xml for permissions and components |
| `extract_strings` | Extract string resources with locale support |
| `list_permissions` | Enumerate all requested permissions |
| `find_smali_references` | Search for patterns in decompiled smali code |
| `get_apk_info` | Get basic APK metadata and information |

### 📋 **Specialized Analysis Prompts**
- **Security Analysis**: Comprehensive vulnerability assessment
- **Privacy Audit**: Data collection and compliance analysis  
- **Reverse Engineering Guide**: Step-by-step analysis workflows

## 📦 Installation

### Prerequisites

**1. Java JDK 8+** (Required by Apktool)
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install default-jdk

# macOS (Homebrew)
brew install openjdk

# Verify installation
java -version
```

**2. Apktool** (Core dependency)
```bash
# Option 1: Package manager (recommended)
# Ubuntu/Debian
sudo apt install apktool

# macOS
brew install apktool

# Option 2: Manual installation
# Download from https://ibotpeaches.github.io/Apktool/install/

# Verify installation
apktool --version
```

**3. Python 3.10+**
```bash
python3 --version  # Should be 3.10 or higher
```

### Setup Instructions

**1. Clone the repository**
```bash
git clone https://github.com/SecFathy/APktool-MCP.git
cd APktool-MCP
```

**2. Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Test the installation**
```bash
python3 apktool_server.py
# Should start the MCP server successfully
```

## ⚙️ Configuration

### Gemini CLI Integration

**1. Install Gemini CLI**
```bash
# Follow instructions at https://github.com/google-gemini/gemini-cli
```

**2. Configure MCP Server**

Edit your Gemini CLI configuration file:
- **Linux/macOS**: `~/.config/gemini-cli/config.json`
- **Windows**: `%APPDATA%\gemini-cli\config.json`

```json
{
  "mcpServers": {
    "apktool": {
      "command": "python3",
      "args": ["/absolute/path/to/apktool_server.py"],
      "env": {
        "APKTOOL_WORK_DIR": "/path/to/workspace"
      }
    }
  }
}
```

### Claude Desktop Integration (Alternative)

Edit Claude Desktop configuration:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "apktool": {
      "command": "python3",
      "args": ["/absolute/path/to/apktool_server.py"],
      "env": {
        "APKTOOL_WORK_DIR": "/path/to/workspace"
      }
    }
  }
}
```

## 🎯 Usage Examples

### Natural Language Commands

```bash
# Start Gemini CLI
gemini

# Security Analysis
> "Analyze the APK at ./suspicious_app.apk for security vulnerabilities"

# Permission Analysis  
> "What permissions does ./myapp.apk request and are any of them dangerous?"

# Code Analysis
> "Find any hardcoded API keys or secrets in ./social_app.apk"

# Privacy Audit
> "Generate a privacy compliance report for ./messenger_app.apk"

# Reverse Engineering
> "Help me understand how the authentication works in ./banking_app.apk"
```

### Direct Tool Usage

```bash
# Decompile an APK
> Use decode_apk to decompile ./sample.apk

# Analyze permissions
> Use list_permissions on the decompiled directory ./sample

# Search for patterns
> Use find_smali_references to search for "crypto" in ./sample

# Extract strings
> Use extract_strings from ./sample for locale "en"

# Rebuild APK
> Use build_apk to recompile ./sample into ./sample_modified.apk
```

### Guided Workflows

```bash
# Run automated security analysis
> Run the security analysis prompt on ./target_app.apk

# Perform privacy audit
> Execute privacy audit workflow for ./social_media_app.apk

# Get reverse engineering guidance
> Use the reverse engineering guide for analyzing login functionality in ./app.apk
```

## 📁 Project Structure

```
apktool-mcp-server/
├── apktool_server.py          # Main MCP server implementation
├── requirements.txt           # Python dependencies
├── config.json               # Example Gemini CLI configuration
├── README.md                 # This file
├── GEMINI.md                 # AI assistant context file
├── LICENSE                   # MIT license
├── examples/                 # Usage examples and samples
│   ├── sample_analysis.py    # Example analysis scripts
│   └── workflows/            # Common workflow examples
├── tests/                    # Unit tests
│   ├── test_server.py        # Server functionality tests
│   └── test_tools.py         # Individual tool tests
└── docs/                     # Additional documentation
    ├── SECURITY.md           # Security guidelines
    ├── CONTRIBUTING.md       # Contribution guidelines
    └── TROUBLESHOOTING.md    # Common issues and solutions
```

## 🔒 Security Considerations

### ⚠️ **Important Security Notes**

- **Legal Compliance**: Only analyze APKs you own or have explicit permission to analyze
- **Malware Risk**: Unknown APKs may contain malicious code - use in isolated environments
- **Data Privacy**: Decompiled APKs may contain sensitive user information
- **Workspace Isolation**: Configure dedicated workspace with restricted permissions
- **Process Limits**: Server includes timeouts to prevent resource exhaustion

### **Best Practices**

```bash
# Use dedicated workspace
export APKTOOL_WORK_DIR="/secure/isolated/workspace"

# Set appropriate permissions
chmod 750 /secure/isolated/workspace

# Monitor resource usage
htop  # Watch memory and CPU during analysis

# Clean up after analysis
rm -rf /secure/isolated/workspace/*
```

## 🧪 Testing

### Run Unit Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=apktool_server tests/
```

### Manual Testing
```bash
# Test server startup
python3 apktool_server.py

# Test with sample APK
# Download a sample APK and test basic functionality
```

### Integration Testing
```bash
# Test Gemini CLI integration
gemini
> /tools  # Should list apktool tools
> Use decode_apk to analyze sample.apk
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone and setup development environment
git clone https://github.com/SecFathy/APktool-MCP.git
cd APktool-MCP
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black apktool_server.py
``` 
