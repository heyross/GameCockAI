# CUDA Setup Guide for GameCock AI

## Overview

GameCock AI supports CUDA acceleration for significantly improved performance when processing financial data and running AI models. This guide will help you set up CUDA support on your system.

## Prerequisites

- NVIDIA GPU with CUDA Compute Capability 3.5 or higher
- Windows 10/11 (64-bit)
- Administrator privileges for installation

## Step 1: Check Your GPU

First, verify that you have a compatible NVIDIA GPU:

1. Open Device Manager
2. Expand "Display adapters"
3. Look for an NVIDIA GPU (e.g., GeForce RTX, Quadro, Tesla)

## Step 2: Install NVIDIA GPU Drivers

1. Visit [NVIDIA Driver Downloads](https://www.nvidia.com/drivers/)
2. Select your GPU model and operating system
3. Download and install the latest drivers
4. Restart your computer

## Step 3: Install CUDA Toolkit

### Option A: CUDA Toolkit (Recommended)

1. Visit [CUDA Toolkit Downloads](https://developer.nvidia.com/cuda-downloads)
2. Select:
   - Operating System: Windows
   - Architecture: x86_64
   - Version: 11.8 or 12.1 (recommended)
3. Download the installer
4. Run the installer as Administrator
5. Follow the installation wizard (default settings are usually fine)

### Option B: CUDA via Conda (Alternative)

If you're using Anaconda/Miniconda:

```bash
conda install cudatoolkit=11.8 -c conda-forge
```

## Step 4: Install PyTorch with CUDA Support

### For CUDA 11.8:
```bash
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### For CUDA 12.1:
```bash
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### For CUDA 12.4:
```bash
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

## Step 5: Verify Installation

Run this Python script to verify CUDA is working:

```python
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"Device count: {torch.cuda.device_count()}")

if torch.cuda.is_available():
    for i in range(torch.cuda.device_count()):
        print(f"Device {i}: {torch.cuda.get_device_name(i)}")
else:
    print("CUDA is not available")
```

Expected output for successful installation:
```
PyTorch version: 2.1.0+cu118
CUDA available: True
CUDA version: 11.8
Device count: 1
Device 0: NVIDIA GeForce RTX 3080
```

## Step 6: Test GameCock AI

1. Run GameCock AI: `python main.py`
2. Look for the startup message: "🚀 CUDA acceleration enabled for optimal performance!"
3. If you see "💻 Running in CPU mode", CUDA is not properly configured

## Troubleshooting

### Common Issues

#### "CUDA is not available" but GPU is detected
- Ensure you have the correct PyTorch version with CUDA support
- Check that CUDA toolkit is properly installed
- Verify environment variables are set correctly

#### "No CUDA-capable device is detected"
- Update your NVIDIA drivers
- Ensure your GPU supports CUDA Compute Capability 3.5+
- Check that the GPU is not being used by another application

#### PyTorch installation fails
- Try installing with `--no-cache-dir` flag
- Use conda instead of pip if pip fails
- Ensure you have sufficient disk space

#### Performance is not improved
- Check that your models are actually using GPU
- Monitor GPU usage with `nvidia-smi`
- Ensure you have enough GPU memory for your workload

### Environment Variables

If CUDA is not detected, you may need to set these environment variables:

```bash
# Add to your system PATH
C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin
C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\libnvvp

# Set CUDA_PATH
CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8
```

### Checking CUDA Installation

You can verify CUDA installation with these commands:

```bash
# Check CUDA version
nvcc --version

# Check GPU status
nvidia-smi

# Check PyTorch CUDA support
python -c "import torch; print(torch.cuda.is_available())"
```

## Performance Benefits

With CUDA enabled, you can expect:

- **3-10x faster** embedding generation
- **2-5x faster** vector database operations
- **Reduced CPU usage** for AI model inference
- **Better scalability** for large datasets

## Support

If you encounter issues:

1. Check the [NVIDIA CUDA Documentation](https://docs.nvidia.com/cuda/)
2. Verify your system meets the requirements
3. Try the troubleshooting steps above
4. Contact support with your system specifications and error messages

## Notes

- CUDA is optional - GameCock AI works perfectly on CPU-only systems
- GPU memory usage depends on model size and batch size
- Some operations may still use CPU even with CUDA enabled
- Consider your GPU memory when processing large datasets
