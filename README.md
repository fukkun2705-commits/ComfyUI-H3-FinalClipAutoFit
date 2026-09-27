# ComfyUI-H3-FinalClipAutoFit

完成映像をPadせず、最終ClipのH3生成尺だけを延長して楽曲終端をカバーするノードです。

- FPS: 24固定
- Motion Context trim: 22 frames固定
- Clip1とClip2以降の既存ワークフローのフレーム計算式をそのまま再現
- `enable_final_fit = true` のときだけ、使用中の最後のClip Durationを必要最小限のH3有効尺へ延長
- IMAGE / LATENT / RTX VSR経路には触れません
