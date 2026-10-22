#!/bin/zsh
# Render every scene and join them with crossfades into out/normgym_intro.mp4.
# Needs ffmpeg, Google Chrome, and puppeteer-core (npm i puppeteer-core in this folder, or set NODE_PATH).
#   ./build.sh            render all scenes, then join
#   ./build.sh --join     only join the existing scene MP4s
set -e
cd "${0:A:h}"
SCENES=(01_open 02_title 03_what 04_demo 03b_norms 05_results 06_social 06b_finetune 07_close)
FADE=0.6

# The example-episode scene is a rendered background (heading, frame, captions) with
# moments from demo.mp4 composited into its frame: [start end] in demo seconds.
DEMO_CLIPS=("1.0 9.5" "24.6 29.2" "69.8 74.8" "100.2 105.4")
DEMO_BOX=(216 127 1488 838)   # x y w h, matching #frame in scenes/04_demo.html
DEMO_START=0.8
DEMO_FADE=0.4
compose_demo() {
  local f="" chain="" prev="" off=0 n=0
  for c in $DEMO_CLIPS; do
    local a=${c% *} b=${c#* }
    f+="[0:v]trim=${a}:${b},setpts=PTS-STARTPTS,fps=30,scale=${DEMO_BOX[3]}:${DEMO_BOX[4]},setsar=1[c$n];"
    if (( n == 0 )); then prev="c0"; off=$(( b - a ))
    else
      off=$(( off - DEMO_FADE ))
      f+="[$prev][c$n]xfade=transition=fade:duration=${DEMO_FADE}:offset=${off}[x$n];"
      prev="x$n"; off=$(( off + b - a ))
    fi
    n=$(( n + 1 ))
  done
  f+="[$prev]format=yuva420p,fade=in:st=0:d=${DEMO_FADE}:alpha=1,setpts=PTS+${DEMO_START}/TB[clip];"
  f+="[1:v][clip]overlay=${DEMO_BOX[1]}:${DEMO_BOX[2]}:eof_action=repeat"
  ffmpeg -y -loglevel error -i demo.mp4 -i out/04_demo_bg.mp4 -filter_complex "$f" \
    -t $(ffprobe -v error -show_entries format=duration -of csv=p=0 out/04_demo_bg.mp4) \
    -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p out/04_demo.mp4
}

if [[ "$1" != "--join" ]]; then
  for s in $SCENES; do
    if [[ $s == 04_demo ]]; then node render.js scenes/$s.html out/04_demo_bg.mp4 &
    else node render.js scenes/$s.html out/$s.mp4 &; fi
  done
  wait
fi
compose_demo

inputs=() filter="" prev="0:v" offset=0
for i in {1..${#SCENES}}; do inputs+=(-i out/${SCENES[$i]}.mp4); done
for i in {2..${#SCENES}}; do
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 out/${SCENES[$((i-1))]}.mp4)
  offset=$(( offset + d - FADE ))
  filter+="[$prev][$((i-1)):v]xfade=transition=fade:duration=$FADE:offset=${offset}[v$i];"
  prev="v$i"
done
ffmpeg -y -loglevel error $inputs -filter_complex "${filter%;}" -map "[$prev]" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -movflags +faststart out/normgym_intro.mp4
echo "-> out/normgym_intro.mp4 ($(ffprobe -v error -show_entries format=duration -of csv=p=0 out/normgym_intro.mp4)s)"
