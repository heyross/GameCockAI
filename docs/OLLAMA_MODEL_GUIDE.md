# 🤖 Ollama Model Management Guide

## Overview
Ollama manages models through a Docker-like system where you can create custom models from base models using Modelfiles. This guide explains the complete workflow for your enhanced Raven model.

## 📁 Model Storage & Management

### Where Models Are Stored
Ollama stores models locally in:
- **Linux/macOS**: `~/.ollama/models/`
- **Windows**: `%USERPROFILE%\.ollama\models\`

### Model Registry
- Models are identified by `name:tag` (default tag is `latest`)
- Base models downloaded from [ollama.ai/library](https://ollama.ai/library)
- Custom models created locally from Modelfiles

## 🛠️ Modelfile Syntax

Your `RavenModelfile` uses these directives:

```dockerfile
FROM mistral                    # Base model to inherit from
SYSTEM """..."""               # System prompt/instructions  
PARAMETER temperature 0.1       # Model inference parameters
PARAMETER top_p 0.9             # Nucleus sampling
PARAMETER stop "<|im_end|>"     # Stop sequences
TEMPLATE """..."""             # Custom prompt template
```

### Key Directives Explained:

#### **FROM**
- Specifies the base model to extend
- Can be local model name or remote model
- Examples: `mistral`, `llama2:7b`, `codellama`

#### **SYSTEM**
- Sets the system prompt that guides model behavior
- Persistent across conversations
- Contains your function mapping and behavioral instructions

#### **PARAMETER**
- Controls model inference behavior
- `temperature`: Randomness (0.0-2.0, lower = more focused)
- `top_p`: Nucleus sampling (0.0-1.0)
- `top_k`: Token selection pool size
- `stop`: Sequences that end generation

#### **TEMPLATE**
- Defines conversation format
- Uses Go template syntax
- Controls how messages are formatted

## 🚀 Complete Deployment Workflow

### Step 1: Create the Enhanced Model
```bash
# Ensure you're in the project directory
cd D:\GitHub\Gamecock_Final

# Create the model (this may take a minute)
ollama create raven-enhanced -f RavenModelfile
```

**What happens:**
- Ollama reads the Modelfile
- Downloads base `mistral` model if not present
- Creates new model with your custom instructions
- Stores as `raven-enhanced:latest`

### Step 2: Verify Model Creation
```bash
# List all models
ollama list

# Expected output:
# NAME                    ID           SIZE    MODIFIED
# mistral:latest          abc123...    4.1GB   2 hours ago
# raven-enhanced:latest def456...    4.1GB   1 minute ago
```

### Step 3: Test the Model
```bash
# Basic test
ollama run raven-enhanced "Hello Raven"

# Analytics test
ollama run raven-enhanced "I want to analyze market trends for credit swaps"
```

### Step 4: Integrate with Application
The code has been updated to use `raven-enhanced` in:
- ✅ `GameCockAI/rag.py` (both ollama.chat calls)
- ✅ `analytics_tools.py` (AI insights generation)

## 🔄 Model Management Commands

### Update/Recreate Model
```bash
# Update the model with changes to Modelfile
ollama create raven-enhanced -f RavenModelfile

# This overwrites the existing model
```

### Remove Model
```bash
# Delete the custom model
ollama rm raven-enhanced

# Remove unused base models
ollama rm mistral
```

### Copy/Rename Model
```bash
# Create a backup
ollama cp raven-enhanced raven-backup

# Create versioned models
ollama cp raven-enhanced raven-v1
```

### Model Information
```bash
# Show detailed model info
ollama show raven-enhanced

# Display the Modelfile used to create it
ollama show raven-enhanced --modelfile
```

## 🧪 Testing Your Enhanced Model

### 1. Function Recognition Test
```bash
ollama run raven-enhanced "Find companies related to banking"
# Expected: Should recognize this as a search_companies intent
```

### 2. Analytics Recognition Test  
```bash
ollama run raven-enhanced "Analyze trading positions for the last month"
# Expected: Should recognize this as analyze_trading_positions intent
```

### 3. Conversation Flow Test
```bash
ollama run raven-enhanced "I want to do some risk analysis but I'm not sure what kind"
# Expected: Should ask clarifying questions
```

## 🔧 Advanced Model Configuration

### Custom Parameters for Different Use Cases
```dockerfile
# For more creative responses
PARAMETER temperature 0.7
PARAMETER top_p 0.9

# For more deterministic/consistent responses  
PARAMETER temperature 0.1
PARAMETER top_k 10

# For faster responses (shorter answers)
PARAMETER max_tokens 512
```

### Multi-Model Setup
You can create specialized models for different purposes:

```bash
# Analytics-focused model
ollama create raven-analytics -f AnalyticsModelfile

# General assistant model  
ollama create raven-general -f GeneralModelfile

# Risk assessment specialist
ollama create raven-risk -f RiskModelfile
```

## 🐛 Troubleshooting

### Model Creation Issues
```bash
# Problem: "model not found"
# Solution: Check base model exists
ollama pull mistral

# Problem: "invalid modelfile"
# Solution: Check syntax and file path
cat RavenModelfile  # Review content
```

### Performance Issues
```bash
# Problem: Model responses too slow
# Solution: Use smaller base model
FROM mistral:7b  # instead of default
```

### Memory Issues
```bash
# Problem: "out of memory"
# Solution: Use quantized models
FROM mistral:7b-q4_0  # 4-bit quantized version
```

## 📊 Model Performance Monitoring

### Check Model Usage
```bash
# Monitor running models
ollama ps

# Expected output when Raven is active:
# NAME               ID       SIZE   PROCESSOR   UNTIL
# raven-enhanced   abc123   4.1GB  GPU         4 minutes from now
```

### Resource Usage
- GPU VRAM: ~4-8GB for 7B models
- System RAM: Additional 2-4GB
- Disk Space: ~4GB per model

## 🔄 Model Versioning Strategy

### Recommended Approach
```bash
# Production model
ollama create raven-prod -f RavenModelfile

# Development model  
ollama create raven-dev -f RavenModelfile-dev

# Experimental features
ollama create raven-experimental -f RavenModelfile-exp
```

### Environment Configuration
```python
# In your application config
import os

MODEL_NAME = os.getenv('SWAPBOT_MODEL', 'raven-enhanced')

# Use in rag.py:
response = ollama.chat(
    model=MODEL_NAME,
    messages=messages,
    tools=tools
)
```

## 🎯 Production Deployment

### 1. Model Validation
```bash
# Run comprehensive tests
python test_enhanced_ai.py

# Verify all functions work
python -c "
import ollama
response = ollama.chat(model='raven-enhanced', messages=[{'role': 'user', 'content': 'Test'}])
print('Model working:', len(response['message']['content']) > 0)
"
```

### 2. Backup Strategy
```bash
# Export model for backup
ollama create raven-backup -f RavenModelfile

# Document the working configuration
ollama show raven-enhanced --modelfile > RavenModelfile.backup
```

### 3. Monitoring Setup
- Monitor response times
- Track function call success rates
- Log any model errors or failures

Your enhanced Raven model is now ready to provide sophisticated financial analysis through natural language interactions! 🚀
