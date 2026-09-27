# ComfyUI-H3-FinalClipAutoFit

A custom node that extends only the MiniMax H3 generation duration of the final active clip to cover the end of the song, without padding the completed video.

- Fixed FPS: **24**
- Fixed Motion Context trim: **22 frames**
- Reproduces the existing workflow's frame calculation for Clip 1 and Clip 2+
- Only when `enable_final_fit = true`, the duration of the last active clip is extended to the minimum valid H3 duration required
- Does not modify the IMAGE / LATENT / RTX VSR paths

## Installation

Clone this repository into `ComfyUI/custom_nodes/`:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/fukkun2705-commits/ComfyUI-H3-FinalClipAutoFit.git
```

Restart ComfyUI after installation.
