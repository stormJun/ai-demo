const appState = {
    direction: 'product_to_dev',
    inputContent: '',
    resultContent: '',
    isTranslating: false,
    cancelStream: null
};

const elements = {
    directionRadios: null,
    inputContent: null,
    charCount: null,
    clearBtn: null,
    translateBtn: null,
    resultEmpty: null,
    resultContent: null,
    resultLoading: null,
    copyBtn: null,
    recognitionResult: null,
    recognitionText: null,
    recognitionSwitch: null
};

function initApp() {
    elements.directionRadios = document.querySelectorAll('input[name="direction"]');
    elements.inputContent = document.getElementById('inputContent');
    elements.charCount = document.getElementById('charCount');
    elements.clearBtn = document.getElementById('clearBtn');
    elements.translateBtn = document.getElementById('translateBtn');
    elements.resultEmpty = document.getElementById('resultEmpty');
    elements.resultContent = document.getElementById('resultContent');
    elements.resultLoading = document.getElementById('resultLoading');
    elements.copyBtn = document.getElementById('copyBtn');
    elements.recognitionResult = document.getElementById('recognitionResult');
    elements.recognitionText = document.getElementById('recognitionText');
    elements.recognitionSwitch = document.getElementById('recognitionSwitch');

    bindEvents();
    checkHealth();
}

function bindEvents() {
    elements.directionRadios.forEach(radio => radio.addEventListener('change', handleDirectionChange));
    elements.inputContent.addEventListener('input', handleInputChange);

    const debouncedRecognize = debounce(handleSceneRecognition, 500);
    elements.inputContent.addEventListener('input', debouncedRecognize);

    elements.clearBtn.addEventListener('click', handleClear);
    elements.translateBtn.addEventListener('click', handleTranslate);
    elements.copyBtn.addEventListener('click', handleCopy);

    if (elements.recognitionSwitch) {
        elements.recognitionSwitch.addEventListener('click', handleRecognitionSwitch);
    }
}

function handleDirectionChange(event) {
    const newDirection = event.target.value;
    if (appState.inputContent || appState.resultContent) {
        if (!confirm('切换翻译方向将清空当前内容,是否继续?')) {
            document.querySelector(`input[value="${appState.direction}"]`).checked = true;
            return;
        }
        handleClear();
    }
    appState.direction = newDirection;
    updatePlaceholder();
}

function handleInputChange() {
    const content = elements.inputContent.value;
    appState.inputContent = content;

    const count = countChars(content);
    elements.charCount.textContent = `已输入 ${count}/5000 字`;

    if (count > 5000) {
        elements.charCount.style.color = '#F5222D';
        elements.translateBtn.disabled = true;
    } else {
        elements.charCount.style.color = '#999';
        elements.translateBtn.disabled = count === 0 || appState.isTranslating;
    }
}

async function handleSceneRecognition() {
    const content = appState.inputContent.trim();
    if (content.length < 10) {
        elements.recognitionResult.style.display = 'none';
        return;
    }

    const result = await recognizeScene(content);
    if (result && result.scene !== 'uncertain' && result.confidence > 0.7) {
        const sceneText = result.scene === 'product_requirement' ? '产品需求' : '技术方案';
        const directionText = result.suggested_direction === 'product_to_dev' ? '产品 → 开发' : '开发 → 产品';
        elements.recognitionText.textContent = `AI识别: 这是【${sceneText}】→ 翻译方向: ${directionText}`;
        elements.recognitionResult.style.display = 'flex';

        if (result.suggested_direction) {
            document.querySelector(`input[value="${result.suggested_direction}"]`).checked = true;
            appState.direction = result.suggested_direction;
            updatePlaceholder();
        }
    } else {
        elements.recognitionResult.style.display = 'none';
    }
}

function handleClear() {
    if (appState.inputContent || appState.resultContent) {
        if (!confirm('确认清空当前内容?')) {
            return;
        }
    }

    if (appState.cancelStream) {
        appState.cancelStream();
        appState.cancelStream = null;
        appState.isTranslating = false;
    }

    elements.inputContent.value = '';
    appState.inputContent = '';

    elements.resultContent.textContent = '';
    appState.resultContent = '';

    elements.charCount.textContent = '已输入 0/5000 字';
    elements.resultEmpty.style.display = 'block';
    elements.resultContent.style.display = 'none';
    elements.resultLoading.style.display = 'none';
    elements.copyBtn.disabled = true;
    elements.translateBtn.disabled = true;
    elements.recognitionResult.style.display = 'none';

    showToast('已清空', 'info');
}

function handleTranslate() {
    const content = appState.inputContent.trim();
    if (!content) {
        showToast('请输入内容后再翻译', 'warning');
        return;
    }
    if (content.length > 5000) {
        showToast('内容过长,请精简至5000字以内', 'error');
        return;
    }
    startTranslation(content, appState.direction);
}

function startTranslation(content, direction) {
    if (appState.cancelStream) {
        appState.cancelStream();
        appState.cancelStream = null;
    }

    appState.isTranslating = true;
    appState.resultContent = '';

    elements.translateBtn.textContent = '翻译中...';
    elements.translateBtn.disabled = true;
    elements.resultEmpty.style.display = 'none';
    elements.resultLoading.style.display = 'flex';
    elements.resultContent.style.display = 'none';
    elements.resultContent.textContent = '';

    translateStream(
        content,
        direction,
        handleTranslateChunk,
        handleTranslateDone,
        handleTranslateError
    ).then(cancel => {
        appState.cancelStream = cancel;
    });
}

function handleTranslateChunk(chunk) {
    if (!appState.resultContent) {
        elements.resultLoading.style.display = 'none';
        elements.resultContent.style.display = 'block';
    }
    appState.resultContent += chunk;
    elements.resultContent.textContent = appState.resultContent;
    elements.resultContent.scrollTop = elements.resultContent.scrollHeight;
}

function handleTranslateDone() {
    appState.isTranslating = false;
    appState.cancelStream = null;
    elements.translateBtn.textContent = '开始翻译';
    elements.translateBtn.disabled = false;
    elements.resultLoading.style.display = 'none';
    elements.resultContent.style.display = 'block';
    elements.copyBtn.disabled = false;
    showToast('翻译完成', 'success');
}

function handleTranslateError(error) {
    appState.isTranslating = false;
    appState.cancelStream = null;
    elements.translateBtn.textContent = '开始翻译';
    elements.translateBtn.disabled = false;
    elements.resultLoading.style.display = 'none';
    elements.resultContent.style.display = 'block';
    elements.resultContent.textContent = `错误: ${error}`;
    showToast(error, 'error');
}

function handleCopy() {
    if (appState.resultContent) {
        copyToClipboard(appState.resultContent);
    }
}

function handleRecognitionSwitch() {
    const newDirection = appState.direction === 'product_to_dev' ? 'dev_to_product' : 'product_to_dev';
    document.querySelector(`input[value="${newDirection}"]`).checked = true;
    appState.direction = newDirection;
    elements.recognitionText.textContent = `手动选择: ${newDirection === 'product_to_dev' ? '产品 → 开发' : '开发 → 产品'}`;
    updatePlaceholder();
}

function updatePlaceholder() {
    const placeholders = {
        product_to_dev: '请输入产品需求描述,例如: 我们需要一个智能推荐功能...',
        dev_to_product: '请输入技术方案说明,例如: 我们优化了数据库查询,QPS提升了30%...'
    };
    elements.inputContent.placeholder = placeholders[appState.direction];
}

async function checkHealth() {
    const health = await healthCheck();
    if (!health || health.status !== 'ok') {
        showToast('服务异常,请联系管理员', 'error');
    }
}

document.addEventListener('DOMContentLoaded', initApp);
