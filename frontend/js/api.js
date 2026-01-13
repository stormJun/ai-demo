const API_BASE_URL = window.API_BASE_URL || 'https://ai-demo-pnm2.vercel.app/api';

/**
 * 流式翻译 API (SSE over fetch)
 * @param {string} content
 * @param {string} direction
 * @param {(chunk:string)=>void} onChunk
 * @param {()=>void} onDone
 * @param {(err:string)=>void} onError
 * @returns {Promise<Function>} cancel function
 */
async function translateStream(content, direction, onChunk, onDone, onError) {
    const controller = new AbortController();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    try {
        const response = await fetch(`${API_BASE_URL}/translate/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content, direction }),
            signal: controller.signal
        });

        if (!response.ok || !response.body) {
            throw new Error(`翻译接口异常: ${response.status}`);
        }

        const reader = response.body.getReader();
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });

            const parts = buffer.split('\n\n');
            buffer = parts.pop() || '';
            parts.forEach(line => {
                if (!line.startsWith('data:')) return;
                try {
                    const payload = JSON.parse(line.replace(/^data:\s*/, ''));
                    if (payload.type === 'content') onChunk(payload.data);
                    else if (payload.type === 'done') onDone();
                    else if (payload.type === 'error') onError(payload.data);
                } catch (e) {
                    onError('数据解析失败');
                }
            });
        }
    } catch (err) {
        if (err.name !== 'AbortError') {
            onError(err.message || '网络连接失败,请检查网络');
        }
    }

    return () => controller.abort();
}

async function recognizeScene(content) {
    try {
        const res = await fetch(`${API_BASE_URL}/recognize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
        });
        if (!res.ok) throw new Error(`识别失败: ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error(err);
        return null;
    }
}

async function healthCheck() {
    try {
        const res = await fetch(`${API_BASE_URL}/health`);
        if (!res.ok) return null;
        return await res.json();
    } catch (err) {
        console.error(err);
        return null;
    }
}
