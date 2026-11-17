#!/bin/bash
# Render all 21 chunks with the proven llama-tts invocation.
# -n 9000 is REQUIRED: this build's default generation cap is 512
# frames (33.5 s) and silently truncates anything longer -- found
# on chunk 02's first strike, corrected here. 9000 frames is the
# model's own 10-minute design ceiling; every chunk stops at its
# text's end token far below it.
LAB=~/workspace/lab/zonos3-mini
BIN=$LAB/bin/llama-b12438/llama-tts
M=$LAB/models/ZONOS3-Mini-Q8_0.gguf
MM=$LAB/models/mmproj-ZONOS3-Mini-F32.gguf
cd ~/workspace/resonance/studio-runs/pirate-essay-audiobook-run1
for f in script/*.txt; do
  name=$(basename "$f" .txt)
  out="chunks/$name.wav"
  if [ -s "$out" ]; then echo "SKIP $name (exists)"; continue; fi
  start=$(date +%s)
  "$BIN" -m "$M" -mm "$MM" --tts-voice Imogen_en-British_F_1 -t 4 \
    -n 9000 -p "$(cat "$f")" -o "$out" 2> "chunks/$name-tts.log"
  rc=$?
  end=$(date +%s)
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out" 2>/dev/null)
  frames=$(grep -oE "generated [0-9]+ frames" "chunks/$name-tts.log" | grep -oE "[0-9]+")
  echo "chunk $name rc=$rc wall=$((end-start))s audio=${dur}s frames=$frames"
done
echo "BATCH DONE"
