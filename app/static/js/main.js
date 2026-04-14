document.addEventListener('DOMContentLoaded', function() {
    // 元素引用
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // PDF相关元素
    const pdfUploadSection = document.getElementById('pdfUploadSection');
    const pdfUploadArea = document.getElementById('pdfUploadArea');
    const pdfFileInput = document.getElementById('pdfFileInput');
    const pdfFileInfo = document.getElementById('pdfFileInfo');
    const pdfFileName = document.getElementById('pdfFileName');
    const removePdfFile = document.getElementById('removePdfFile');
    const startPdfProcess = document.getElementById('startPdfProcess');
    const pdfProgressSection = document.getElementById('pdfProgressSection');
    const pdfProgressBar = document.getElementById('pdfProgressBar').querySelector('.progress-bar');
    const pdfStatusMessage = document.getElementById('pdfStatusMessage');
    
    // 图片相关元素
    const imageUploadArea = document.getElementById('imageUploadArea');
    const imageFileInput = document.getElementById('imageFileInput');
    const imageFileInfo = document.getElementById('imageFileInfo');
    const imageFileName = document.getElementById('imageFileName');
    const removeImageFile = document.getElementById('removeImageFile');
    
    const processSection = document.getElementById('processSection');
    const resultsSection = document.getElementById('resultsSection');
    const ollamaUrl = document.getElementById('ollamaUrl');
    const checkOllama = document.getElementById('checkOllama');
    const ollamaStatus = document.getElementById('ollamaStatus');
    const modelSelect = document.getElementById('modelSelect');
    const startProcess = document.getElementById('startProcess');
    const progressBar = document.getElementById('progressBar').querySelector('.progress-bar');
    const statusMessage = document.getElementById('statusMessage');
    const downloadTxt = document.getElementById('downloadTxt');
    const ocrContent = document.getElementById('ocrContent');
    const newTask = document.getElementById('newTask');
    
    // 变量
    let uploadedFile = null;
    let fileType = ''; // 'pdf' 或 'image'
    let fileUrl = null;
    let ocrResults = null;
    let isProcessing = false;
    let currentTaskId = null;
    let pollingInterval = null;
    
    // 页面加载时获取用户配置
    loadConfig();
    
    // 显示加载状态
    function showLoading(element) {
        element.disabled = true;
        element.innerHTML = '<span class="loading">处理中...</span>';
    }
    
    // 隐藏加载状态
    function hideLoading(element, originalText) {
        element.disabled = false;
        element.innerHTML = originalText;
    }
    
    // 显示错误消息
    function showError(message) {
        alert('错误: ' + message);
    }
    
    // 标签页切换功能
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tab = this.getAttribute('data-tab');
            
            // 切换标签按钮状态
            tabBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // 切换标签内容
            tabContents.forEach(content => {
                content.style.display = 'none';
            });
            document.getElementById(tab + '-tab').style.display = 'block';
            
            // 重置文件选择
            resetFileSelection();
        });
    });
    
    // 模型选择变化时保存配置
    modelSelect.addEventListener('change', function() {
        const url = ollamaUrl.value;
        const model = this.value;
        if (url && model) {
            saveConfig(url, model);
        }
    });
    
    // 重置文件选择
    function resetFileSelection() {
        uploadedFile = null;
        fileType = '';
        
        // 重置PDF文件选择
        pdfFileInput.value = '';
        pdfFileInfo.style.display = 'none';
        startPdfProcess.style.display = 'none';
        pdfUploadSection.style.display = 'block';
        pdfProgressSection.style.display = 'none';
        
        // 重置图片文件选择
        imageFileInput.value = '';
        imageFileInfo.style.display = 'none';
        
        // 重置其他部分
        processSection.style.display = 'none';
        resultsSection.style.display = 'none';
        
        // 重置进度条和状态消息
        progressBar.style.width = '0%';
        statusMessage.textContent = '';
        statusMessage.className = 'status';
        pdfProgressBar.style.width = '0%';
        pdfStatusMessage.textContent = '';
        pdfStatusMessage.className = 'status';
    }
    
    // PDF文件上传处理
    pdfFileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            uploadedFile = e.target.files[0];
            fileType = 'pdf';
            pdfFileName.textContent = uploadedFile.name;
            pdfFileInfo.style.display = 'block';
            startPdfProcess.style.display = 'inline-block';
            processSection.style.display = 'none';
            resultsSection.style.display = 'none';
            
            // 重置进度条和状态消息
            progressBar.style.width = '0%';
            statusMessage.textContent = '';
            statusMessage.className = 'status';
        }
    });
    
    // 图片文件上传处理
    imageFileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            uploadedFile = e.target.files[0];
            fileType = 'image';
            imageFileName.textContent = uploadedFile.name;
            imageFileInfo.style.display = 'block';
            processSection.style.display = 'none';
            resultsSection.style.display = 'none';
            
            // 重置进度条和状态消息
            progressBar.style.width = '0%';
            statusMessage.textContent = '';
            statusMessage.className = 'status';
        }
    });
    
    // PDF拖放功能
    pdfUploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        pdfUploadArea.style.borderColor = '#667eea';
        pdfUploadArea.style.backgroundColor = '#f9f9ff';
    });
    
    pdfUploadArea.addEventListener('dragleave', function() {
        pdfUploadArea.style.borderColor = '#ddd';
        pdfUploadArea.style.backgroundColor = 'white';
    });
    
    pdfUploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        pdfUploadArea.style.borderColor = '#ddd';
        pdfUploadArea.style.backgroundColor = 'white';
        
        if (e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            if (file.type === 'application/pdf') {
                uploadedFile = file;
                fileType = 'pdf';
                pdfFileName.textContent = file.name;
                pdfFileInfo.style.display = 'block';
                startPdfProcess.style.display = 'inline-block';
                processSection.style.display = 'none';
                resultsSection.style.display = 'none';
                
                // 重置进度条和状态消息
                progressBar.style.width = '0%';
                statusMessage.textContent = '';
                statusMessage.className = 'status';
            } else {
                showError('请上传PDF文件');
            }
        }
    });
    
    // 图片拖放功能
    imageUploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        imageUploadArea.style.borderColor = '#667eea';
        imageUploadArea.style.backgroundColor = '#f9f9ff';
    });
    
    imageUploadArea.addEventListener('dragleave', function() {
        imageUploadArea.style.borderColor = '#ddd';
        imageUploadArea.style.backgroundColor = 'white';
    });
    
    imageUploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        imageUploadArea.style.borderColor = '#ddd';
        imageUploadArea.style.backgroundColor = 'white';
        
        if (e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            const imageTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/bmp', 'image/gif'];
            if (imageTypes.includes(file.type)) {
                uploadedFile = file;
                fileType = 'image';
                imageFileName.textContent = file.name;
                imageFileInfo.style.display = 'block';
                processSection.style.display = 'none';
                resultsSection.style.display = 'none';
                
                // 重置进度条和状态消息
                progressBar.style.width = '0%';
                statusMessage.textContent = '';
                statusMessage.className = 'status';
            } else {
                showError('请上传图片文件');
            }
        }
    });
    
    // 移除PDF文件
    removePdfFile.addEventListener('click', function() {
        uploadedFile = null;
        fileType = '';
        pdfFileInput.value = '';
        pdfFileInfo.style.display = 'none';
        startPdfProcess.style.display = 'none';
        pdfUploadSection.style.display = 'block';
        pdfProgressSection.style.display = 'none';
        processSection.style.display = 'none';
        resultsSection.style.display = 'none';
        
        // 重置进度条和状态消息
        progressBar.style.width = '0%';
        statusMessage.textContent = '';
        statusMessage.className = 'status';
        pdfProgressBar.style.width = '0%';
        pdfStatusMessage.textContent = '';
        pdfStatusMessage.className = 'status';
    });
    
    // 移除图片文件
    removeImageFile.addEventListener('click', function() {
        uploadedFile = null;
        fileType = '';
        imageFileInput.value = '';
        imageFileInfo.style.display = 'none';
        processSection.style.display = 'none';
        resultsSection.style.display = 'none';
        
        // 重置进度条和状态消息
        progressBar.style.width = '0%';
        statusMessage.textContent = '';
        statusMessage.className = 'status';
    });
    
    // 开始处理PDF
    startPdfProcess.addEventListener('click', function() {
        console.log('开始处理PDF');
        
        if (!uploadedFile) {
            showError('请先上传PDF文件');
            return;
        }
        
        if (!modelSelect.value) {
            showError('请选择模型');
            return;
        }
        
        console.log('文件信息:', uploadedFile.name, uploadedFile.size, uploadedFile.type);
        console.log('模型:', modelSelect.value);
        console.log('Ollama URL:', ollamaUrl.value);
        
        // 隐藏上传部分，显示进度部分
        pdfUploadSection.style.display = 'none';
        pdfProgressSection.style.display = 'block';
        
        // 重置进度条和状态消息
        pdfProgressBar.style.width = '0%';
        pdfStatusMessage.textContent = '上传PDF文件中...';
        pdfStatusMessage.className = 'status';
        
        // 上传文件
        const formData = new FormData();
        formData.append('file', uploadedFile);
        
        console.log('开始上传文件');
        
        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            console.log('上传响应状态:', response.status, response.statusText);
            if (!response.ok) {
                throw new Error('上传文件失败: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            console.log('上传响应数据:', data);
            if (data.status === 'success') {
                const fileUrl = data.file_path;
                console.log('文件路径:', fileUrl);
                pdfStatusMessage.textContent = 'PDF上传成功，开始拆分图片...';
                pdfProgressBar.style.width = '30%';
                
                // 执行OCR
                console.log('开始执行OCR');
                return fetch('/api/ocr', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        file_path: fileUrl,
                        model: modelSelect.value,
                        ollama_url: ollamaUrl.value
                    })
                });
            } else {
                throw new Error(data.message || '上传文件失败');
            }
        })
        .then(response => {
            console.log('OCR响应状态:', response.status, response.statusText);
            if (!response.ok) {
                throw new Error('OCR处理失败: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            console.log('OCR响应数据:', data);
            if (data.status === 'success') {
                currentTaskId = data.task_id;
                console.log('任务ID:', currentTaskId);
                
                // 开始轮询获取进度
                pollingInterval = setInterval(() => {
                    fetch(`/api/ocr/progress/${currentTaskId}`)
                        .then(response => response.json())
                        .then(progressData => {
                            console.log('进度数据:', progressData);
                            if (progressData.status === 'success') {
                                const progress = progressData.progress;
                                
                                // 更新进度条和状态消息
                                pdfProgressBar.style.width = `${progress.progress}%`;
                                pdfStatusMessage.textContent = progress.message;
                                
                                // 检查任务是否完成
                                if (progress.status === 'completed') {
                                    clearInterval(pollingInterval);
                                    pdfStatusMessage.className = 'status success';
                                    
                                    // 显示结果
                                    resultsSection.style.display = 'block';
                                    downloadTxt.href = `/api/download?file_path=${encodeURIComponent(progress.result.txt_path)}`;
                                    
                                    // 显示OCR内容（前500个字符）
                                    let content = '';
                                    progress.result.ocr_results.forEach(item => {
                                        content += item.text + '\n\n';
                                    });
                                    ocrContent.textContent = content.length > 500 ? content.substring(0, 500) + '...' : content;
                                } else if (progress.status === 'error') {
                                    clearInterval(pollingInterval);
                                    pdfStatusMessage.className = 'status error';
                                    showError(progress.message);
                                } else if (progress.status === 'stopped') {
                                    clearInterval(pollingInterval);
                                    pdfStatusMessage.className = 'status error';
                                    showError('任务已停止');
                                }
                            }
                        })
                        .catch(error => {
                            console.error('获取进度失败:', error);
                            clearInterval(pollingInterval);
                            pdfStatusMessage.textContent = `获取进度失败: ${error.message}`;
                            pdfStatusMessage.className = 'status error';
                        });
                }, 2000); // 每2秒轮询一次
            } else {
                throw new Error(data.message || 'OCR处理失败');
            }
        })
        .catch(error => {
            console.error('处理失败:', error);
            pdfStatusMessage.textContent = `处理失败: ${error.message}`;
            pdfStatusMessage.className = 'status error';
            pdfProgressBar.style.width = '0%';
            showError(error.message);
        });
    });
    
    // 停止处理PDF
    const stopPdfProcess = document.getElementById('stopPdfProcess');
    stopPdfProcess.addEventListener('click', function() {
        if (!currentTaskId) {
            showError('没有正在进行的任务');
            return;
        }
        
        console.log('停止处理任务:', currentTaskId);
        
        // 发送停止请求
        fetch(`/api/ocr/stop/${currentTaskId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            console.log('停止响应状态:', response.status, response.statusText);
            if (!response.ok) {
                throw new Error('停止任务失败: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            console.log('停止响应数据:', data);
            if (data.status === 'success') {
                console.log('任务已停止');
                // 清除轮询
                if (pollingInterval) {
                    clearInterval(pollingInterval);
                    pollingInterval = null;
                }
                // 显示停止消息
                pdfStatusMessage.textContent = '任务已停止';
                pdfStatusMessage.className = 'status error';
            } else {
                throw new Error(data.message || '停止任务失败');
            }
        })
        .catch(error => {
            console.error('停止任务失败:', error);
            showError(error.message);
        });
    });
    
    // 检查Ollama服务
    checkOllama.addEventListener('click', function() {
        const url = ollamaUrl.value;
        ollamaStatus.textContent = '检查中...';
        ollamaStatus.className = 'status';
        
        const originalText = checkOllama.innerHTML;
        showLoading(checkOllama);
        
        fetch(`/api/ollama/check?url=${encodeURIComponent(url)}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    ollamaStatus.textContent = data.message;
                    ollamaStatus.className = 'status success';
                    
                    // 获取模型列表
                    return fetch(`/api/ollama/models?url=${encodeURIComponent(url)}`);
                } else {
                    throw new Error(data.message);
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    modelSelect.innerHTML = '';
                    
                    // 获取用户配置中的首选模型
                    return fetch('/api/config/get')
                        .then(configResponse => configResponse.json())
                        .then(configData => {
                            const preferredModel = configData.status === 'success' ? configData.config.model : '';
                            let hasPreferredModel = false;
                            
                            data.models.forEach(model => {
                                const option = document.createElement('option');
                                option.value = model.name;
                                option.textContent = model.name;
                                if (model.name === preferredModel) {
                                    option.selected = true;
                                    hasPreferredModel = true;
                                }
                                modelSelect.appendChild(option);
                            });
                            
                            // 如果没有首选模型，选择第一个模型
                            if (!hasPreferredModel && data.models.length > 0) {
                                modelSelect.selectedIndex = 0;
                            }
                            
                            modelSelect.disabled = false;
                            
                            // 只有在有上传文件的情况下才显示处理部分
                            if (uploadedFile) {
                                processSection.style.display = 'block';
                            }
                            
                            // 保存当前配置
                            const selectedModel = modelSelect.value;
                            saveConfig(url, selectedModel);
                        });
                } else {
                    throw new Error(data.message);
                }
            })
            .catch(error => {
                ollamaStatus.textContent = error.message;
                ollamaStatus.className = 'status error';
                modelSelect.disabled = true;
                processSection.style.display = 'none';
            })
            .finally(() => {
                hideLoading(checkOllama, originalText);
            });
    });
    
    // 开始处理
    startProcess.addEventListener('click', function() {
        if (isProcessing) return;
        
        if (!uploadedFile) {
            showError('请先上传文件');
            return;
        }
        
        if (!modelSelect.value) {
            showError('请选择模型');
            return;
        }
        
        isProcessing = true;
        const originalText = startProcess.innerHTML;
        showLoading(startProcess);
        
        // 上传文件
        const formData = new FormData();
        formData.append('file', uploadedFile);
        
        statusMessage.textContent = '上传文件中...';
        statusMessage.className = 'status';
        progressBar.style.width = '20%';
        
        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('上传文件失败: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                fileUrl = data.file_path;
                statusMessage.textContent = '文件上传成功，开始OCR处理...';
                progressBar.style.width = '40%';
                
                // 执行OCR
                return fetch('/api/ocr', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        file_path: fileUrl,
                        model: modelSelect.value,
                        ollama_url: ollamaUrl.value
                    })
                });
            } else {
                throw new Error(data.message || '上传文件失败');
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('OCR处理失败: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                ocrResults = data.result;
                statusMessage.textContent = 'OCR处理完成';
                statusMessage.className = 'status success';
                progressBar.style.width = '100%';
                
                // 显示结果
                displayResults();
            } else {
                throw new Error(data.message || 'OCR处理失败');
            }
        })
        .catch(error => {
            statusMessage.textContent = `处理失败: ${error.message}`;
            statusMessage.className = 'status error';
            progressBar.style.width = '0%';
            showError(error.message);
        })
        .finally(() => {
            isProcessing = false;
            hideLoading(startProcess, originalText);
        });
    });
    
    // 显示结果
    function displayResults() {
        resultsSection.style.display = 'block';
        
        // 设置下载链接
        downloadTxt.href = `/api/download?file_path=${encodeURIComponent(ocrResults.txt_path)}`;
        
        // 显示OCR内容（前500个字符）
        let content = '';
        ocrResults.ocr_results.forEach(item => {
            content += item.text + '\n\n';
        });
        ocrContent.textContent = content.length > 500 ? content.substring(0, 500) + '...' : content;
    }
    
    // 新任务
    newTask.addEventListener('click', function() {
        resetFileSelection();
        progressBar.style.width = '0%';
        statusMessage.textContent = '';
    });
    
    // 加载用户配置
    function loadConfig() {
        fetch('/api/config/get')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const config = data.config;
                    if (config.url) {
                        ollamaUrl.value = config.url;
                    }
                    if (config.model) {
                        // 先检查模型是否存在，如果存在则选择
                        checkOllama.click();
                    }
                }
            })
            .catch(error => {
                console.error('加载配置失败:', error);
            });
    }
    
    // 保存用户配置
    function saveConfig(url, model) {
        fetch('/api/config/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: url,
                model: model
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status !== 'success') {
                console.error('保存配置失败:', data.message);
            }
        })
        .catch(error => {
            console.error('保存配置失败:', error);
        });
    }
});
