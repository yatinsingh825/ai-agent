
# 🚀 AI Call Agent - Error Recovery & Resilience System



> A production-grade error recovery and resilience system for AI-powered call agents, featuring intelligent retry mechanisms, circuit breakers, and comprehensive observability.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Design Decisions](#design-decisions)
- [Project Structure](#project-structure)
- [Monitoring & Observability](#monitoring--observability)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This system provides a robust, production-ready error handling framework for AI call agents that depend on multiple third-party services (ElevenLabs TTS, LLM providers, CRM APIs). It implements industry-standard resilience patterns including:

- **Intelligent Retry Logic** with exponential backoff
- **Circuit Breaker Pattern** to prevent cascading failures
- **Health Check System** for automatic service recovery
- **Multi-Channel Alerting** for critical failures
- **Comprehensive Logging** for debugging and analytics
- **Graceful Degradation** to maintain partial functionality

### 🎥 Demo

```bash
# Run the complete assignment scenario
python main.py
# Select option  for full demo [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/55715455/27885014-5d32-4026-8bb3-6594aad27c0a/image.jpg)
```

**Expected Output:**
```
Contact 1: ❌ 503 Error → Retry (5s) → Retry (10s) → Retry (20s) → Failed → Alert → Next
Contact 2: ✅ Service Recovered → Success
Contact 3: ✅ Success
```

---

## ✨ Features

### 1️⃣ Custom Exception Hierarchy

Intelligent error categorization for proper handling:

| Exception Type | Description | Retry? | Use Cases |
|---------------|-------------|--------|-----------|
| `TransientError` | Temporary failures | ✅ Yes | Network timeouts, 503 errors, rate limits |
| `PermanentError` | Unrecoverable errors | ❌ No | Authentication failures, invalid payloads |
| `CircuitBreakerOpenError` | Service unavailable | ❌ No | Circuit breaker in OPEN state |

```python
# Example: Automatic classification
try:
    response = service.call()
except ServiceUnavailableError:  # TransientError
    # Automatically retried with backoff
except AuthenticationError:      # PermanentError
    # Fails immediately, sends alert
```

### 2️⃣ Retry Logic with Exponential Backoff

Configurable retry mechanism that prevents overwhelming failing services:

```python
RetryHandler(
    initial_delay=5,           # Start with 5 second delay
    max_attempts=3,            # Maximum 3 retry attempts
    backoff_multiplier=2       # Double delay each time (5s → 10s → 20s)
)
```

**Flow:**
```
Attempt 1 fails → Wait 5s  → Retry
Attempt 2 fails → Wait 10s → Retry
Attempt 3 fails → Wait 20s → Retry
Max retries exceeded → Alert & Fail
```

### 3️⃣ Circuit Breaker Pattern

Implements the **Closed → Open → Half-Open** state machine:

```
┌─────────────┐
│   CLOSED    │  ← Normal operation
│ (Healthy)   │
└──────┬──────┘
       │ 3 consecutive failures
       ▼
┌─────────────┐
│    OPEN     │  ← Fast-fail mode
│ (Unhealthy) │
└──────┬──────┘
       │ After 60s timeout
       ▼
┌─────────────┐
│ HALF-OPEN   │  ← Testing recovery
│ (Testing)   │
└──────┬──────┘
       │ Success → CLOSED
       │ Failure → OPEN
```

**Benefits:**
- ⚡ **Fast-fail** when service is down (no wasted retries)
- 🔄 **Automatic recovery** detection
- 🛡️ **Prevents cascading failures** to dependent systems

### 4️⃣ Health Check System

Background monitoring with automatic recovery:

```python
# Periodic health checks every 30 seconds
health_check_manager.register_service("ElevenLabs", check_function)
health_check_manager.start()

# Automatic state updates:
# Unhealthy → Healthy: Log recovery + Reset circuit breaker
# Healthy → Unhealthy: Log degradation
```

### 5️⃣ Comprehensive Logging & Observability

Multi-destination logging for different audiences:

| Destination | Format | Audience | Purpose |
|------------|--------|----------|---------|
| **Local File** | JSON | Engineers | Debugging, analytics |
| **Google Sheets** | Tabular | Non-technical teams | Business visibility |
| **Console** | Formatted | Operators | Real-time monitoring |

**Log Schema:**
```json
{
  "timestamp": "2026-01-29T23:24:32.159",
  "service_name": "ElevenLabs",
  "error_category": "TRANSIENT_ERROR",
  "retry_count": 2,
  "circuit_breaker_state": "CLOSED",
  "message": "Service unavailable (503)"
}
```

### 6️⃣ Multi-Channel Alerting

Critical failures trigger alerts across multiple channels:

```
Circuit Breaker Opens
         ↓
    ┌────┴────┐
    │ Alerting │
    └────┬────┘
         ├─→ 📧 Email (SMTP)
         ├─→ 💬 Telegram Bot
         └─→ 🔗 Webhook (Slack/Discord/PagerDuty)
```

**Alert Triggers:**
- Circuit breaker opens
- Call permanently fails after max retries
- Service stays down beyond threshold (5 minutes)

### 7️⃣ Graceful Degradation

System continues operating even when services fail:

```
Contact 1: ElevenLabs fails → Skip → Next contact
Contact 2: ElevenLabs recovered → Process successfully
Contact 3: Process successfully

Result: 2/3 contacts processed (66% success rate)
```

---

## 🏗️ Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                     AI Call Agent                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │ Contact Queue│      │ Health Checks│                   │
│  └──────┬───────┘      └──────┬───────┘                   │
│         │                     │                            │
│         ▼                     ▼                            │
│  ┌─────────────────────────────────────┐                  │
│  │      Resilience Layer               │                  │
│  │  ┌────────────┐  ┌────────────┐    │                  │
│  │  │  Retry     │  │  Circuit   │    │                  │
│  │  │  Handler   │  │  Breaker   │    │                  │
│  │  └────────────┘  └────────────┘    │                  │
│  └───────────┬─────────────────────────┘                  │
│              ▼                                             │
│  ┌─────────────────────────────────────┐                  │
│  │    External Services                │                  │
│  │  ┌────────────┐  ┌────────────┐    │                  │
│  │  │ ElevenLabs │  │    LLM     │    │                  │
│  │  │    TTS     │  │  Provider  │    │                  │
│  │  └────────────┘  └────────────┘    │                  │
│  └───────────┬─────────────────────────┘                  │
│              ▼                                             │
│  ┌─────────────────────────────────────┐                  │
│  │   Observability Layer               │                  │
│  │  ┌─────┐  ┌─────┐  ┌─────┐         │                  │
│  │  │Logs │  │Alert│  │Health│         │                  │
│  │  └─────┘  └─────┘  └─────┘         │                  │
│  └─────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

### Error Flow Diagram

```
┌─────────────┐
│   Request   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│ Circuit Breaker State Check     │
├─────────────────────────────────┤
│ CLOSED/HALF_OPEN │ OPEN         │
└────────┬─────────┴──────┬───────┘
         │                │
         ▼                ▼
    ┌─────────┐      ┌─────────┐
    │ Execute │      │Fail Fast│
    │ Request │      │  Alert  │
    └────┬────┘      └─────────┘
         │
         ▼
    ┌─────────────────────────┐
    │ Success? │ TransientErr?│
    └────┬──────┴───────┬──────┘
         │              │
         ▼              ▼
    ┌────────┐   ┌────────────┐
    │  Log   │   │Retry Logic │
    │Success │   │Exponential │
    └────────┘   │  Backoff   │
                 └──────┬─────┘
                        │
                 ┌──────┴──────┐
                 │ PermanentErr│
                 └──────┬──────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ Update CB    │
                 │ Send Alert   │
                 │ Log Event    │
                 │ Next Contact │
                 └──────────────┘
```

---

## 📦 Installation

### Prerequisites

- **Python 3.8+**
- **pip** package manager
- **Git** (for cloning)

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/ai-call-agent.git
cd ai-call-agent

# 2. Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install project as editable package
pip install -e .

# 5. Configure environment variables
cp .env.example .env
# Edit .env with your credentials
```

### Dependencies

```txt
requests>=2.31.0          # HTTP client
python-dotenv>=1.0.0      # Environment variable management
gspread>=5.12.0           # Google Sheets integration (optional)
oauth2client>=4.1.3       # Google OAuth (optional)
python-telegram-bot>=20.7 # Telegram alerts (optional)
```

---

## ⚡ Quick Start

### Interactive Mode

```bash
python main.py
```

**Menu Options:**
1. **Normal Call** - Test successful execution
2. **Simulate 503** - Test error handling & retry
3. **View Status** - Check circuit breaker states
4. **Reset** - Reset all circuit breakers
5. **Full Demo** - Run complete assignment scenario ⭐
6. **Exit**

### Programmatic Usage

```python
from main import AICallAgent

# Initialize agent
agent = AICallAgent()

# Make a call
contact = {"name": "John Doe", "phone": "+1234567890"}
result = agent.make_single_call(contact, simulate_503=False)

print(f"Call status: {result['status']}")
```

---

## ⚙️ Configuration

### Environment Variables (`.env`)

```env
# ===== Email Configuration =====
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password      # Use app-specific password
EMAIL_RECEIVER=admin@company.com

# ===== Telegram Configuration =====
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789

# ===== Webhook Configuration =====
WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# ===== Google Sheets (Optional) =====
GOOGLE_SHEETS_CREDS=credentials.json
GOOGLE_SHEETS_NAME=Error Recovery Logs
```

### Runtime Configuration (`config/config.py`)

```python
class Config:
    # Retry settings
    RETRY_INITIAL_DELAY = 5          # seconds
    RETRY_MAX_ATTEMPTS = 3           # attempts
    RETRY_BACKOFF_MULTIPLIER = 2     # exponential factor
    
    # Circuit breaker settings
    CIRCUIT_BREAKER_FAILURE_THRESHOLD = 3  # failures before opening
    CIRCUIT_BREAKER_TIMEOUT = 60           # seconds in OPEN state
    CIRCUIT_BREAKER_HALF_OPEN_ATTEMPTS = 1 # test attempts in HALF_OPEN
    
    # Health check settings
    HEALTH_CHECK_INTERVAL = 30       # seconds between checks
    HEALTH_CHECK_TIMEOUT = 5         # seconds per check
    
    # Logging
    LOG_FILE_PATH = "logs/error_logs.json"
```

**Tuning Guide:**

| Parameter | Low Traffic | High Traffic | Production |
|-----------|-------------|--------------|------------|
| `RETRY_INITIAL_DELAY` | 5s | 2s | 3s |
| `RETRY_MAX_ATTEMPTS` | 3 | 2 | 3 |
| `FAILURE_THRESHOLD` | 3 | 5 | 5 |
| `CIRCUIT_TIMEOUT` | 60s | 30s | 45s |

---

## 🎮 Usage

### Scenario 1: Normal Operation

```bash
# Start agent
python main.py

# Select option  - Normal Call [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/55715455/b5377886-9b38-4211-a6c3-bfddec123992/Incubation-2.pdf)
Enter your choice: 1

# Output:
✓ LLM Response: "Hello, this is your call script"
✓ Audio URL: https://mock-audio-url.com/default
✓ Duration: 5.2s
✅ CALL COMPLETED SUCCESSFULLY
```

### Scenario 2: 503 Error with Retry

```bash
# Select option  - Simulate 503 Error [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/55715455/8ef66341-e898-4538-a4d7-974fa1e012d0/image.jpg)
Enter your choice: 2

# Output:
[Step 1] ✓ LLM response generated
[Step 2] Converting to speech...
⚠️  503 Service Unavailable detected
→ Retry attempt 1/3 (waiting 5s)...
→ Retry attempt 2/3 (waiting 10s)...
→ Retry attempt 3/3 (waiting 20s)...
❌ Max retries exceeded
📧 Alert sent to admin@company.com
💬 Telegram notification sent
🔗 Webhook triggered
```

### Scenario 3: Complete Assignment Demo

```bash
# Select option  - Run Complete 503 Scenario [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/55715455/27885014-5d32-4026-8bb3-6594aad27c0a/image.jpg)
Enter your choice: 5

# Demonstrates:
# - Contact 1: Fails with 503, retries, alerts, moves to next
# - Contact 2: Succeeds (service recovered)
# - Contact 3: Succeeds
# - Proper logging and circuit breaker behavior
```

### Scenario 4: Monitoring

```bash
# Select option  - View Circuit Breaker Status [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/55715455/e6cd6b37-f250-43c2-a2c2-9c344ac8e1af/image.jpg)
Enter your choice: 3

# Output:
======================================================================
CIRCUIT BREAKER STATUS
======================================================================
ElevenLabs           : CLOSED
LLM                  : CLOSED
======================================================================
```

---

## 🧪 Testing

### Run Individual Test Suites

```bash
# Test retry handler
python -m tests.test_retry

# Expected: 4 tests (success, transient retry, permanent no-retry, max retries)

# Test circuit breaker
python -m tests.test_circuit_breaker

# Expected: 4 tests (closed state, opens after failures, half-open, recovery)

# Test ElevenLabs service
python -m tests.test_elevenlabs

# Expected: 4 tests (success, 503 error, recovery, health check)

# Test complete flow
python -m tests.test_complete_flow

# Expected: Full 503 scenario demonstration
```

### Test Coverage

| Component | Test File | Coverage |
|-----------|-----------|----------|
| Retry Handler | `test_retry.py` | ✅ 100% |
| Circuit Breaker | `test_circuit_breaker.py` | ✅ 100% |
| ElevenLabs Service | `test_elevenlabs.py` | ✅ 100% |
| Complete Flow | `test_complete_flow.py` | ✅ Scenario |

### Manual Testing Checklist

- [ ] Normal call succeeds without errors
- [ ] 503 error triggers retry with backoff (5s, 10s, 20s)
- [ ] Circuit breaker opens after 3 failures
- [ ] Alerts sent on critical failures
- [ ] Health checks detect recovery
- [ ] Circuit breaker closes after recovery
- [ ] Logs written to `logs/error_logs.json`
- [ ] Graceful degradation (moves to next contact)

---

## 🎨 Design Decisions

### 1. **No External Retry/Circuit Breaker Libraries**

**Why?** 
- ✅ Assignment requirement (no Resilience4j, Tenacity, Polly)
- ✅ Full control over behavior
- ✅ Educational value
- ✅ No unnecessary dependencies

**Implementation:**
- Built from scratch using standard library
- Thread-safe using `threading.Lock`
- Configurable parameters

### 2. **Separation of Concerns**

```
exceptions/     → Domain-specific errors
core/          → Resilience patterns (retry, CB)
services/      → External service integration
loggers/       → Observability
alerts/        → Notification channels
```

**Benefits:**
- 🧩 Modular, testable components
- 🔄 Easy to swap implementations
- 📈 Scalable architecture

### 3. **Configuration-Driven Behavior**

All parameters centralized in `config/config.py`:

```python
Config.RETRY_MAX_ATTEMPTS = 3  # Change retry limit
Config.CIRCUIT_BREAKER_TIMEOUT = 60  # Adjust timeout
```

**Benefits:**
- 🎛️ No code changes for tuning
- 🧪 Easy A/B testing
- 🚀 Environment-specific configs

### 4. **Mock External Services**

Services return mock data instead of real API calls:

```python
def text_to_speech(self, text: str):
    return {
        "audio_url": "https://mock-audio-url.com/audio.mp3",
        "status": "success"
    }
```

**Benefits:**
- ⚡ Fast testing (no network calls)
- 💰 No API costs
- 🎭 Controllable failure simulation

### 5. **Structured JSON Logging**

```json
{"timestamp": "...", "service": "...", "error_category": "..."}
```

**Benefits:**
- 🔍 Easy parsing and analysis
- 📊 Integration with log aggregators (ELK, Splunk)
- 🤖 Machine-readable for automation

---

## 📁 Project Structure

```
ai-call-agent/
│
├── 📂 config/                    # Configuration management
│   ├── __init__.py
│   └── config.py                 # Centralized settings
│
├── 📂 core/                      # Core resilience patterns
│   ├── __init__.py
│   ├── retry_handler.py          # Exponential backoff retry logic
│   ├── circuit_breaker.py        # Circuit breaker implementation
│   └── health_check.py           # Background health monitoring
│
├── 📂 services/                  # External service integrations
│   ├── __init__.py
│   ├── external_service.py       # Base service class
│   ├── elevenlabs_service.py     # ElevenLabs TTS integration
│   └── llm_service.py            # LLM provider integration
│
├── 📂 exceptions/                # Custom exception hierarchy
│   ├── __init__.py
│   └── custom_exceptions.py      # Transient/Permanent errors
│
├── 📂 loggers/                   # Logging implementations
│   ├── __init__.py
│   ├── file_logger.py            # JSON file logging
│   └── sheets_logger.py          # Google Sheets logging
│
├── 📂 alerts/                    # Alert notification channels
│   ├── __init__.py
│   ├── email_alert.py            # SMTP email alerts
│   ├── telegram_alert.py         # Telegram bot notifications
│   └── webhook_alert.py          # Generic webhook integration
│
├── 📂 tests/                     # Standalone test suites
│   ├── __init__.py
│   ├── test_retry.py             # Retry handler tests
│   ├── test_circuit_breaker.py   # Circuit breaker tests
│   ├── test_elevenlabs.py        # ElevenLabs service tests
│   └── test_complete_flow.py     # End-to-end scenario tests
│
├── 📂 logs/                      # Generated log files
│   └── error_logs.json           # Structured JSON logs
│
├── 📄 main.py                    # Main application entry point
├── 📄 setup.py                   # Package installation config
├── 📄 requirements.txt           # Python dependencies
├── 📄 .env                       # Environment variables (gitignored)
├── 📄 .env.example               # Example environment file
├── 📄 .gitignore                 # Git ignore rules
├── 📄 README.md                  # This file
└── 📄 LICENSE                    # MIT License
```

---

## 📊 Monitoring & Observability

### Logs

**Location:** `logs/error_logs.json`

**View logs:**
```bash
# View all logs
cat logs/error_logs.json

# View last 10 entries
tail -n 10 logs/error_logs.json

# Filter errors
cat logs/error_logs.json | grep "TRANSIENT_ERROR"
```

**Sample log entry:**
```json
{
  "timestamp": "2026-01-29T23:24:32.159",
  "service_name": "ElevenLabs",
  "error_category": "TRANSIENT_ERROR",
  "retry_count": 2,
  "circuit_breaker_state": "CLOSED",
  "message": "Service unavailable (503)"
}
```

### Metrics

Key metrics to monitor:

| Metric | Formula | Threshold |
|--------|---------|-----------|
| **Error Rate** | `Failed Calls / Total Calls` | < 5% |
| **Retry Success Rate** | `Retries Succeeded / Total Retries` | > 70% |
| **Circuit Breaker Opens** | `Count(CB State = OPEN)` | < 3/hour |
| **Average Retry Count** | `Sum(Retries) / Total Calls` | < 1.5 |
| **Service Recovery Time** | `Time(OPEN → CLOSED)` | < 2 min |

### Alerts

**Critical Alerts:**
- 🔴 Circuit breaker opened
- 🔴 Service down > 5 minutes
- 🔴 Error rate > 10%

**Warning Alerts:**
- 🟡 Retry rate > 30%
- 🟡 Single service latency > 5s

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

### Development Setup

```bash
# Fork and clone
git clone https://github.com/yourusername/ai-call-agent.git
cd ai-call-agent

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and test
python -m tests.test_retry
python -m tests.test_circuit_breaker

# Commit with conventional commits
git commit -m "feat: add new retry strategy"

# Push and create PR
git push origin feature/amazing-feature
```

### Code Style

- Follow **PEP 8** style guide
- Use **type hints** for function signatures
- Write **docstrings** for all public methods
- Keep functions **< 50 lines**
- **100% test coverage** for new features

