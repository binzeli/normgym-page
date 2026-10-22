// Render a scene page to MP4 (or stills) by seeking it frame by frame in headless Chrome.
// Usage:
//   node render.js scenes/01_open.html out/01_open.mp4 [--fps 30]
//   node render.js scenes/01_open.html out/stills --stills 1.5,9,14.6
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const puppeteer = require('puppeteer-core');

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

(async () => {
  const [, , htmlArg, outArg, ...rest] = process.argv;
  const opt = {};
  for (let i = 0; i < rest.length; i += 2) opt[rest[i].replace(/^--/, '')] = rest[i + 1];
  const fps = Number(opt.fps || 30);

  const browser = await puppeteer.launch({ executablePath: CHROME, headless: true });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(htmlArg), { waitUntil: 'networkidle0' });
  await page.evaluate(() => document.fonts.ready);
  const duration = await page.evaluate(() => window.DURATION);

  if (opt.stills) {
    fs.mkdirSync(outArg, { recursive: true });
    const base = path.basename(htmlArg, '.html');
    for (const t of opt.stills.split(',').map(Number)) {
      await page.evaluate((t) => window.seek(t), t);
      await page.screenshot({ path: path.join(outArg, `${base}_${t.toFixed(1)}s.png`) });
    }
  } else {
    fs.mkdirSync(path.dirname(outArg), { recursive: true });
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps),
      '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', outArg],
      { stdio: ['pipe', 'inherit', 'inherit'] });
    const frames = Math.round(duration * fps);
    for (let i = 0; i < frames; i++) {
      await page.evaluate((t) => window.seek(t), i / fps);
      const buf = await page.screenshot({ type: 'png', optimizeForSpeed: true });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
      if (i % 150 === 0) process.stdout.write(`\r${path.basename(htmlArg)}: ${i}/${frames}`);
    }
    ff.stdin.end();
    await new Promise((r) => ff.on('close', r));
    console.log(`\r${path.basename(htmlArg)}: ${frames}/${frames} -> ${outArg}`);
  }
  await browser.close();
})();
