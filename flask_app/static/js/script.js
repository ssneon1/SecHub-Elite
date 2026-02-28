document.addEventListener('DOMContentLoaded', () => {
    // =============================================
    // DOM References
    // =============================================
    const hudButtons = document.querySelectorAll('.hud-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    const form = document.getElementById('lab-form');
    const toolSelect = document.getElementById('tool-select');
    const hostInput = document.getElementById('host-input');
    const hostGroup = document.getElementById('host-group');
    const portInput = document.getElementById('port-input');
    const extraInput = document.getElementById('extra-input');
    const extraLabel = document.getElementById('extra-label');
    const paramsRow = document.getElementById('params-row');
    const terminal = document.getElementById('terminal');
    const runBtn = document.getElementById('run-btn');
    const stopBtn = document.getElementById('stop-btn');
    const clearBtn = document.getElementById('clear-btn');

    // Monitor elements
    const streamStatus = document.getElementById('stream-status');
    const packetLog = document.getElementById('packet-log');
    const statConnections = document.getElementById('stat-connections');
    const statSuccess = document.getElementById('stat-success');
    const statErrors = document.getElementById('stat-errors');
    const statWarnings = document.getElementById('stat-warnings');
    const statElapsed = document.getElementById('stat-elapsed');

    // =============================================
    // State
    // =============================================
    let activeAbortController = null;
    let monitorStats = { total: 0, success: 0, errors: 0, warnings: 0, packetNum: 0 };
    let elapsedTimer = null;
    let startTime = null;

    // =============================================
    // HUD Tab Switching
    // =============================================
    hudButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.getAttribute('data-tab');
            hudButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            tabPanes.forEach(pane => {
                pane.classList.remove('active');
                if (pane.id === `tab-${target}`) pane.classList.add('active');
            });
        });
    });

    // =============================================
    // Tool Selection — Dynamic UI
    // =============================================
    if (toolSelect) {
        toolSelect.addEventListener('change', () => {
            const val = toolSelect.value;
            if (val === 'slowloris') {
                extraLabel.textContent = 'Sockets';
                extraInput.value = '150';
                hostGroup.classList.remove('hidden');
                paramsRow.classList.remove('hidden');
            } else if (val === 'hping') {
                extraLabel.textContent = 'Protocol';
                extraInput.value = 'tcp';
                hostGroup.classList.remove('hidden');
                paramsRow.classList.remove('hidden');
            } else {
                hostGroup.classList.add('hidden');
                paramsRow.classList.add('hidden');
            }
        });
    }

    // =============================================
    // Monitor Helpers
    // =============================================
    const classifyLog = (text) => {
        const t = text.trim();
        if (t.startsWith('[+]')) return 'success';
        if (t.startsWith('[!]')) return 'error';
        if (t.startsWith('[~]') || t.toLowerCase().includes('warn')) return 'warning';
        if (text.toLowerCase().includes('success') || text.includes('PASSED') || text.includes('connected')) return 'success';
        if (text.toLowerCase().includes('fail') || text.toLowerCase().includes('error')) return 'error';
        return 'info';
    };

    const updatePacketTable = (data, classification) => {
        if (!packetLog) return;

        const placeholder = packetLog.querySelector('.empty-row');
        if (placeholder) placeholder.remove();

        monitorStats.packetNum++;
        monitorStats.total++;
        if (classification === 'success') monitorStats.success++;
        else if (classification === 'error') monitorStats.errors++;
        else if (classification === 'warning') monitorStats.warnings++;

        if (statConnections) statConnections.textContent = monitorStats.total;
        if (statSuccess) statSuccess.textContent = monitorStats.success;
        if (statErrors) statErrors.textContent = monitorStats.errors;
        if (statWarnings) statWarnings.textContent = monitorStats.warnings;

        const rowClass = { success: 'row-ok', error: 'row-err', warning: 'row-warn', info: '' }[classification] || '';
        const cellClass = { success: 'status-ok', error: 'status-err', warning: 'status-warn', info: 'status-info' }[classification] || '';
        const label = { success: '[+] OK', error: '[!] ERR', warning: '[~] WARN', info: '[*] INFO' }[classification] || '[*] INFO';

        const tool = toolSelect ? toolSelect.value.toUpperCase() : 'SYS';
        const host = hostInput && hostInput.value ? hostInput.value : '—';
        const ts = new Date().toLocaleTimeString([], { hour12: false });
        const info = data.text.length > 55 ? data.text.slice(0, 55) + '…' : data.text;

        const tr = document.createElement('tr');
        tr.className = rowClass;
        tr.innerHTML = `
            <td>${monitorStats.packetNum}</td>
            <td>${ts}</td>
            <td>${host}</td>
            <td>${tool}</td>
            <td title="${data.text.replace(/"/g, '&quot;')}">${info}</td>
            <td class="${cellClass}">${label}</td>
        `;
        packetLog.appendChild(tr);
        if (packetLog.parentElement) packetLog.parentElement.scrollTop = packetLog.parentElement.scrollHeight;
    };

    const startMonitor = () => {
        monitorStats = { total: 0, success: 0, errors: 0, warnings: 0, packetNum: 0 };
        if (statConnections) statConnections.textContent = '0';
        if (statSuccess) statSuccess.textContent = '0';
        if (statErrors) statErrors.textContent = '0';
        if (statWarnings) statWarnings.textContent = '0';
        if (statElapsed) statElapsed.textContent = '00:00';
        if (packetLog) packetLog.innerHTML = '<tr class="empty-row"><td colspan="6">Initializing capture...</td></tr>';

        if (streamStatus) {
            streamStatus.textContent = 'ACTIVE';
            streamStatus.className = 'stream-badge active';
        }

        if (elapsedTimer) clearInterval(elapsedTimer);
        startTime = Date.now();
        elapsedTimer = setInterval(() => {
            const s = Math.floor((Date.now() - startTime) / 1000);
            const m = Math.floor(s / 60).toString().padStart(2, '0');
            const sec = (s % 60).toString().padStart(2, '0');
            if (statElapsed) statElapsed.textContent = `${m}:${sec}`;
        }, 1000);
    };

    const stopMonitor = () => {
        if (elapsedTimer) { clearInterval(elapsedTimer); elapsedTimer = null; }
        if (streamStatus) {
            streamStatus.textContent = 'DONE';
            streamStatus.className = 'stream-badge done';
        }
    };

    // =============================================
    // Terminal Logger
    // =============================================
    const addLog = (data) => {
        if (!terminal) return;
        const placeholder = terminal.querySelector('.terminal-placeholder');
        if (placeholder) placeholder.remove();

        const line = document.createElement('div');
        line.className = 'log-line';
        const ts = data.timestamp || new Date().toLocaleTimeString([], { hour12: false });
        const colorClass = data.color ? `text-${data.color}` : '';
        const boldClass = data.bold ? 'text-bold' : '';

        line.innerHTML = `
            <span class="log-ts">[${ts}]</span>
            <span class="log-text ${colorClass} ${boldClass}">${data.text}</span>
        `;
        terminal.appendChild(line);
        terminal.scrollTop = terminal.scrollHeight;

        // Mirror to monitor
        updatePacketTable(data, classifyLog(data.text));
    };

    const resetUI = () => {
        if (runBtn) runBtn.classList.remove('hidden');
        if (stopBtn) stopBtn.classList.add('hidden');
        stopMonitor();
    };

    // =============================================
    // Execution Engine — Form Submit
    // =============================================
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            startMonitor();
            activeAbortController = new AbortController();

            const payload = {
                tool: toolSelect ? toolSelect.value : 'slowloris',
                host: hostInput ? hostInput.value : '',
                port: portInput ? portInput.value : '80',
                extra: extraInput ? extraInput.value : ''
            };

            if (runBtn) runBtn.classList.add('hidden');
            if (stopBtn) stopBtn.classList.remove('hidden');

            addLog({ text: `BOOTING ${payload.tool.toUpperCase()} MODULE...`, color: 'warning', bold: true });

            try {
                const response = await fetch('/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                    signal: activeAbortController.signal
                });

                if (!response.ok) {
                    const err = await response.json().catch(() => ({ error: 'Unknown error' }));
                    addLog({ text: `CRITICAL ERROR: ${err.error}`, color: 'error' });
                    resetUI();
                    return;
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const events = buffer.split('\n\n');
                    buffer = events.pop(); // keep partial

                    events.forEach(event => {
                        const trimmed = event.trim();
                        if (!trimmed.startsWith('data: ')) return;

                        const parts = trimmed.split('\ndata: ');
                        parts.forEach(part => {
                            try {
                                const jsonStr = part.replace(/^data:\s*/, '').trim();
                                if (jsonStr) addLog(JSON.parse(jsonStr));
                            } catch (_) { /* ignore malformed chunks */ }
                        });
                    });
                }

                addLog({ text: 'SEQUENCE COMPLETED SUCCESSFULLY.', color: 'success', bold: true });

            } catch (err) {
                if (err.name === 'AbortError') {
                    addLog({ text: 'OPERATION ABORTED BY OPERATOR.', color: 'error', bold: true });
                } else {
                    addLog({ text: `UPLINK FAILURE: ${err.message}`, color: 'error' });
                }
            } finally {
                resetUI();
                activeAbortController = null;
            }
        });
    }

    // =============================================
    // Stop Button
    // =============================================
    if (stopBtn) {
        stopBtn.addEventListener('click', () => {
            if (activeAbortController) activeAbortController.abort();
        });
    }

    // =============================================
    // Clear Button
    // =============================================
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            if (terminal) {
                terminal.innerHTML = `
                    <div class="terminal-placeholder">
                        <i data-lucide="radio" class="fade-icon"></i>
                        <p>Establishing uplink...</p>
                    </div>
                `;
                lucide.createIcons();
            }
        });
    }
});
