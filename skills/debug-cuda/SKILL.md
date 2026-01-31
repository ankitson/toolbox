# Debug CUDA / GPU Issues

## When to use
The user reports CUDA not working, `torch.cuda.is_available()` returning False, or GPU acceleration failures — even though `nvidia-smi` shows the GPU.

## Key insight
`nvidia-smi` and CUDA compute use different libraries. `nvidia-smi` uses `libnvidia-ml` (management). PyTorch/CUDA programs use `libcuda` (compute). One can work while the other is broken.

## Diagnostic steps

### 1. Check if it's a host or container issue
Run on the **host** first — not inside Docker:
```bash
python3 -c "
import ctypes
lib = ctypes.CDLL('libcuda.so')
r = lib.cuInit(0)
print('cuInit:', r)
"
```
- `cuInit: 0` = host is fine, problem is container-specific
- `cuInit: 999` = host driver is broken, no point debugging inside containers

### 2. If host cuInit returns 999 (CUDA_ERROR_UNKNOWN)
Most common cause: **kernel module / userspace library version mismatch** after a kernel update or partial driver update without rebooting.

Verify:
```bash
cat /proc/driver/nvidia/version   # kernel module version
nvidia-smi | head -3              # userspace library version
uname -r                          # current kernel
```

Fix: **reboot**. Or try without reboot:
```bash
sudo rmmod nvidia_uvm && sudo modprobe nvidia_uvm
# or
sudo nvidia-persistenced
```

### 3. If host is fine but container fails
Check in order:

**a) Is the GPU passed to the container?**
```bash
docker exec <container> nvidia-smi
```
If this fails, the container doesn't have GPU access. Check `docker-compose.yaml` for `runtime: nvidia` or `deploy.resources.reservations.devices`.

**b) Are CUDA libraries findable?**
```bash
docker exec <container> ldconfig -p | grep -E "libcuda|libcudart"
docker exec <container> echo $LD_LIBRARY_PATH
```
If `libcudart` is missing from ldconfig, add `/usr/local/cuda/lib64` to `LD_LIBRARY_PATH`.

**c) Is PyTorch using the right Python / venv?**
```bash
docker exec <container> bash -lc 'which python && python -c "import torch; print(torch.version.cuda)"'
```
- If `torch.version.cuda` prints `None` → CPU-only PyTorch was installed
- If it prints a version (e.g. `12.8`) → PyTorch has CUDA support, problem is elsewhere

**d) CUDA / PyTorch version mismatch?**
```bash
nvcc --version          # toolkit version in container
nvidia-smi | head -3    # driver CUDA version
python -c "import torch; print(torch.version.cuda)"  # PyTorch CUDA version
```
All three should be compatible. The driver CUDA version must be >= the toolkit version.

### 4. cuInit error code reference
- `0` = success
- `1` = CUDA_ERROR_INVALID_VALUE
- `2` = CUDA_ERROR_OUT_OF_MEMORY
- `3` = CUDA_ERROR_NOT_INITIALIZED
- `100` = CUDA_ERROR_NO_DEVICE (no GPU visible)
- `101` = CUDA_ERROR_INVALID_DEVICE
- `999` = CUDA_ERROR_UNKNOWN (driver broken, reboot usually fixes)

## Common root causes (ranked by frequency)
1. **Needs reboot** — kernel updated, driver module stale (cuInit 999)
2. **CPU-only PyTorch installed** — pip/uv resolved to wrong wheel
3. **LD_LIBRARY_PATH not set** — CUDA libs not findable at runtime
4. **GPU not passed to container** — missing `--gpus all` or compose equivalent
5. **CUDA version mismatch** — toolkit too new for installed driver
