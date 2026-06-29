// Mirrors the CLI's rendering: same palette and Rec. 601 luma weights, a
// centered square crop, and a spring-based reveal in the spirit of harmonica.

const PALETTE = [' ', '.', '.', '/', 'c', '(', '@', '#', '8'];

function paletteChar(red, green, blue) {
  const value = blue * 0.1145 + green * 0.5866 + red * 0.2989;
  let index = Math.floor(value / (256 / PALETTE.length)) % PALETTE.length;
  if (index < 0) index += PALETTE.length;
  return PALETTE[index];
}

// --- Minimal syntax highlighting (no dependencies) ---

function escapeHtml(text) {
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

const PYTHON_KEYWORDS = new Set([
  'def', 'return', 'if', 'elif', 'else', 'for', 'while', 'in', 'break', 'continue',
  'pass', 'import', 'from', 'as', 'with', 'try', 'except', 'finally', 'class', 'and',
  'or', 'not', 'is', 'None', 'True', 'False', 'lambda', 'yield', 'global', 'raise',
]);
const PYTHON_BUILTINS = new Set([
  'min', 'max', 'int', 'float', 'len', 'range', 'print', 'map', 'sorted', 'abs',
  'round', 'enumerate', 'bool', 'str', 'list', 'dict', 'tuple', 'set', 'open',
]);

// Return an array (one entry per character) of token class names, or null.
function pythonCharClasses(code) {
  const classes = new Array(code.length).fill(null);
  const fill = (start, end, name) => {
    for (let k = start; k < end; k += 1) classes[k] = name;
  };

  let i = 0;
  while (i < code.length) {
    const char = code[i];

    if (char === '#') {
      let j = i;
      while (j < code.length && code[j] !== '\n') j += 1;
      fill(i, j, 'com');
      i = j;
    } else if (char === '"' || char === "'") {
      let j = i + 1;
      while (j < code.length) {
        if (code[j] === '\\') {
          j += 2;
        } else if (code[j] === char) {
          j += 1;
          break;
        } else {
          j += 1;
        }
      }
      fill(i, j, 'str');
      i = j;
    } else if (char >= '0' && char <= '9') {
      let j = i;
      while (j < code.length && /[0-9.]/.test(code[j])) j += 1;
      fill(i, j, 'num');
      i = j;
    } else if (/[A-Za-z_]/.test(char)) {
      let j = i;
      while (j < code.length && /[A-Za-z0-9_]/.test(code[j])) j += 1;
      const word = code.slice(i, j);
      let name = null;
      if (PYTHON_KEYWORDS.has(word)) name = 'kw';
      else if (PYTHON_BUILTINS.has(word)) name = 'bui';
      else if (code[j] === '(') name = 'fn';
      if (name) fill(i, j, name);
      i = j;
    } else {
      i += 1;
    }
  }
  return classes;
}

// Render the first `count` characters of code as highlighted HTML.
function renderHighlighted(code, classes, count) {
  let html = '';
  let current = null;
  let buffer = '';
  const flush = () => {
    if (!buffer) return;
    html += current ? `<span class="hl-${current}">${escapeHtml(buffer)}</span>` : escapeHtml(buffer);
    buffer = '';
  };
  for (let k = 0; k < count; k += 1) {
    if (classes[k] !== current) {
      flush();
      current = classes[k];
    }
    buffer += code[k];
  }
  flush();
  return html;
}

// Light shell highlighting for the install block: comments, command, flags.
function highlightShell(code) {
  return code
    .split('\n')
    .map((line) => {
      const indent = line.match(/^\s*/)[0];
      const rest = line.slice(indent.length);
      if (rest.startsWith('#')) {
        return `${indent}<span class="hl-com">${escapeHtml(rest)}</span>`;
      }
      if (!rest) return line;

      let seenCommand = false;
      const tokens = rest.split(/(\s+)/).map((token) => {
        if (!token || /^\s+$/.test(token)) return token;
        if (!seenCommand) {
          seenCommand = true;
          return `<span class="hl-cmd">${escapeHtml(token)}</span>`;
        }
        if (token.startsWith('-')) return `<span class="hl-flag">${escapeHtml(token)}</span>`;
        return escapeHtml(token);
      });
      return indent + tokens.join('');
    })
    .join('\n');
}

const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// Spring reveal: a damped harmonic oscillator (the model harmonica implements),
// integrated with semi-implicit Euler. Under-damped, so it overshoots gently.
function revealOnLoad() {
  const items = Array.from(document.querySelectorAll('.reveal'));

  if (reducedMotion) {
    items.forEach((element) => {
      element.style.opacity = '1';
    });
    return;
  }

  const stiffness = 170;
  const damping = 17;
  const dt = 1 / 60;

  items.forEach((element, order) => {
    let position = 26;
    let velocity = 0;
    const startAt = performance.now() + order * 90;

    element.style.opacity = '0';

    function frame(now) {
      if (now < startAt) {
        requestAnimationFrame(frame);
        return;
      }

      const acceleration = -stiffness * position - damping * velocity;
      velocity += acceleration * dt;
      position += velocity * dt;

      element.style.transform = `translateY(${position.toFixed(2)}px)`;
      element.style.opacity = Math.max(0, Math.min(1, 1 - Math.abs(position) / 26)).toFixed(3);

      if (Math.abs(position) < 0.1 && Math.abs(velocity) < 0.1) {
        element.style.transform = '';
        element.style.opacity = '1';
        return;
      }
      requestAnimationFrame(frame);
    }

    requestAnimationFrame(frame);
  });
}

// Copy-to-clipboard for the install command.
function setupCopy() {
  const button = document.getElementById('copy');
  const command = document.getElementById('install');
  if (!button || !command) return;

  button.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(command.textContent.trim());
      const previous = button.textContent;
      button.textContent = 'copied';
      setTimeout(() => {
        button.textContent = previous;
      }, 1400);
    } catch {
      button.textContent = 'press ⌘/ctrl+c';
    }
  });
}

// In-browser webcam → ASCII demo.
function setupDemo() {
  const screen = document.getElementById('screen');
  const startButton = document.getElementById('start');
  const stopButton = document.getElementById('stop');
  const status = document.getElementById('status');
  const positionSegment = document.getElementById('screen-pos');

  const video = document.createElement('video');
  video.playsInline = true;
  video.muted = true;
  video.setAttribute('playsinline', '');

  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d', { willReadFrequently: true });

  let stream = null;
  let timer = null;
  let columns = 0;
  let rows = 0;

  function setStatus(text, live) {
    status.textContent = text;
    status.dataset.live = live ? 'true' : 'false';
  }

  function measureGrid() {
    const probe = document.createElement('span');
    probe.textContent = 'M';
    probe.style.cssText = 'position:absolute;visibility:hidden;white-space:pre';
    screen.appendChild(probe);
    const rect = probe.getBoundingClientRect();
    screen.removeChild(probe);

    const cellWidth = rect.width || 6;
    const cellHeight = rect.height || 10;
    const available = screen.clientWidth - 24;

    let cols = Math.min(Math.floor(available / cellWidth), 120);
    let rws = Math.round(cols / 2);

    const maxRows = Math.floor((window.innerHeight * 0.6) / cellHeight);
    if (rws > maxRows) {
      rws = maxRows;
      cols = rws * 2;
    }

    columns = Math.max(24, cols);
    rows = Math.max(12, rws);
    canvas.width = columns;
    canvas.height = rows;
    if (positionSegment) positionSegment.textContent = `${columns}×${rows}`;
  }

  function renderFrame() {
    const width = video.videoWidth;
    const height = video.videoHeight;
    if (!width || !height) return;

    const side = Math.min(width, height);
    const sourceX = (width - side) / 2;
    const sourceY = (height - side) / 2;

    // Mirror horizontally for a natural selfie view.
    context.save();
    context.scale(-1, 1);
    context.drawImage(video, sourceX, sourceY, side, side, -columns, 0, columns, rows);
    context.restore();

    const pixels = context.getImageData(0, 0, columns, rows).data;
    let output = '';
    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < columns; x++) {
        const offset = (y * columns + x) * 4;
        output += paletteChar(pixels[offset], pixels[offset + 1], pixels[offset + 2]);
      }
      output += '\n';
    }
    screen.textContent = output;
  }

  async function start() {
    setStatus('● …', false);
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user' },
        audio: false,
      });
      video.srcObject = stream;
      await video.play();
      measureGrid();
      screen.style.display = 'block';
      timer = setInterval(renderFrame, 1000 / 24);
      setStatus('● LIVE', true);
      startButton.hidden = true;
      stopButton.hidden = false;
    } catch (error) {
      setStatus(`✗ ${error.name || 'NO CAM'}`, false);
    }
  }

  function stop() {
    if (timer) clearInterval(timer);
    timer = null;
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      stream = null;
    }
    setStatus('○ IDLE', false);
    if (positionSegment) positionSegment.textContent = '0×0';
    startButton.hidden = false;
    stopButton.hidden = true;
  }

  let resizeTimer = null;
  window.addEventListener('resize', () => {
    if (!stream) return;
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(measureGrid, 150);
  });

  startButton.addEventListener('click', start);
  stopButton.addEventListener('click', stop);
  window.addEventListener('pagehide', stop);
}

// Type each feature snippet out, character by character, when it scrolls in.
function typeInto(element, delay) {
  const code = element.dataset.text || '';
  const classes = pythonCharClasses(code);
  let index = 0;
  function step() {
    element.innerHTML = renderHighlighted(code, classes, index);
    if (index < code.length) {
      index += 1;
      setTimeout(step, 26 + Math.random() * 28);
    }
  }
  setTimeout(step, delay);
}

const NVIM_ROWS = 6;

// Build the Neovim chrome around a snippet: relative line-number gutter and
// end-of-buffer tildes. Reserves the code height so the layout never jumps.
function decorateNvim(snippet) {
  const lines = (snippet.dataset.code || '').split('\n');
  const buffer = snippet.closest('.nvim__buf');
  const codeColumn = snippet.closest('.nvim__code');
  if (!buffer || !codeColumn) return;

  snippet.style.minHeight = `${lines.length * 1.5}em`;

  // The typing caret ends on the last line, so that's where the cursor lives.
  const cursorRow = lines.length - 1;

  const gutter = document.createElement('div');
  gutter.className = 'nvim__gutter';
  for (let row = 0; row < NVIM_ROWS; row += 1) {
    const cell = document.createElement('div');
    if (row < lines.length) {
      cell.textContent = row === cursorRow ? String(lines.length) : String(Math.abs(cursorRow - row));
      if (row === cursorRow) cell.className = 'cur';
    } else {
      cell.innerHTML = '&nbsp;';
    }
    gutter.appendChild(cell);
  }
  buffer.insertBefore(gutter, buffer.firstChild);

  // Keep the statusline position in sync with the cursor's real line:column.
  const nvim = snippet.closest('.nvim');
  const positionSegment = nvim && nvim.querySelector('.nvim__status .nvim__seg:last-child');
  if (positionSegment) {
    const lastLine = lines[cursorRow] || '';
    positionSegment.textContent = `${lines.length}:${Math.max(1, lastLine.length)}`;
  }

  if (lines.length < NVIM_ROWS) {
    const eob = document.createElement('div');
    eob.className = 'nvim__eob';
    for (let row = lines.length; row < NVIM_ROWS; row += 1) {
      const tilde = document.createElement('div');
      tilde.textContent = '~';
      eob.appendChild(tilde);
    }
    codeColumn.appendChild(eob);
  }
}

function setupTyping() {
  const snippets = Array.from(document.querySelectorAll('.snip'));
  if (!snippets.length) return;

  const staticRender = reducedMotion || !('IntersectionObserver' in window);

  snippets.forEach((snippet) => {
    const code = snippet.dataset.code || '';
    snippet.dataset.text = code;
    decorateNvim(snippet);
    snippet.innerHTML = staticRender
      ? renderHighlighted(code, pythonCharClasses(code), code.length)
      : '';
  });

  if (staticRender) return;

  const observer = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        typeInto(entry.target, Math.random() * 220);
      });
    },
    { threshold: 0.4 },
  );

  snippets.forEach((snippet) => observer.observe(snippet));
}

// Highlight the install/usage shell block(s).
function setupUsage() {
  document.querySelectorAll('.code').forEach((block) => {
    block.innerHTML = highlightShell(block.textContent);
  });
}

revealOnLoad();
setupCopy();
setupDemo();
setupUsage();
setupTyping();
