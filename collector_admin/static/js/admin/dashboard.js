// 全局状态管理
const state = {
    isRunning: false,
    requestInterval: 60,
    currentTaskId: null,
    taskConfig: null,
    errorMessage: '',
    lastRequestTime: null,
    nextRequestTime: null
};

// 表格分页功能
const PAGE_SIZE = 10;  // 每页显示的行数
let currentPage = 1;
let allTasks = [];

// 页面初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeState();
    initializeSelects();
    initializeProducts();
    initializeTable();  // 添加表格初始化
    
    // 初始化状态
    refreshStatus();
    
    // 立即执行一次更新
    updateTaskList();
    
    // 设置定时刷新
    setInterval(refreshStatus, 10000);
    setInterval(updateTaskList, 30000);
});

// 初始化状态
function initializeState() {
    // 从注入的script标签中读取初始数据
    const initialDataElement = document.getElementById('initial-data');
    if (initialDataElement) {
        try {
            const INITIAL_DATA = JSON.parse(initialDataElement.textContent);
            state.isRunning = INITIAL_DATA.isRunning;
            updateButtonsState();
        } catch (error) {
            console.error('解析初始数据失败:', error);
        }
    }
}

// 初始化选择框
function initializeSelects() {
    // 初始化服务器选择框
    const serverSelect = document.getElementById('serverSelect');
    if (serverSelect) {
        Object.entries(SERVERS).forEach(([id, name]) => {
            const option = document.createElement('option');
            option.value = id;
            option.textContent = `${name} (${id})`;
            serverSelect.appendChild(option);
        });
    }

    // 初始化商品选择框
    const productSelect = document.getElementById('productSelect');
    if (productSelect) {
        // 按照定义的顺序添加分组
        GROUP_ORDER.forEach(groupName => {
            const productIds = PRODUCT_GROUPS[groupName];
            if (productIds && productIds.length > 0) {
                const optgroup = document.createElement('optgroup');
                optgroup.label = groupName;
                
                productIds.forEach(id => {
                    const productName = PRODUCT_TYPES[id];
                    if (productName) {
                        const option = document.createElement('option');
                        option.value = id;
                        option.textContent = `${productName} (${id})`;
                        optgroup.appendChild(option);
                    }
                });
                
                if (optgroup.children.length > 0) {
                    productSelect.appendChild(optgroup);
                }
            }
        });
    }

    // 初始化商品分组菜单
    const productGroupMenu = document.getElementById('productGroupMenu');
    if (productGroupMenu) {
        // 使用相同的分组顺序
        GROUP_ORDER.forEach(groupName => {
            const productIds = PRODUCT_GROUPS[groupName];
            if (productIds && productIds.length > 0) {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.className = 'dropdown-item';
                a.href = '#';
                a.textContent = groupName;
                a.onclick = (e) => {
                    e.preventDefault();
                    selectProductGroup(groupName, productIds);
                };
                li.appendChild(a);
                productGroupMenu.appendChild(li);
            }
        });
    }
}

// 采集器控制
async function startCollector() {
    try {
        const response = await fetch('/admin/collector/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ is_running: true })
        });

        const result = await response.json();
        if (!response.ok) throw new Error(result.message || '启动失败');

        state.isRunning = true;
        updateButtonsState();
        showMessage('采集器已启动', 'success');
    } catch (error) {
        console.error('启动采集器失败:', error);
        showMessage(error.message || '启动失败，请查看控制台获取详细信息', 'error');
    }
}

async function stopCollector() {
    try {
        const response = await fetch('/admin/collector/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ is_running: false })
        });

        const result = await response.json();
        if (!response.ok) throw new Error(result.message || '停止失败');

        state.isRunning = false;
        updateButtonsState();
        showMessage('采集器已停止', 'success');
    } catch (error) {
        console.error('停止采集器失败:', error);
        showMessage(error.message || '停止失败，请查看控制台获取详细信息', 'error');
    }
}

// UI更新函数
function updateButtonsState() {
    const startBtn = document.querySelector('button[onclick="startCollector()"]');
    const stopBtn = document.querySelector('button[onclick="stopCollector()"]');
    const intervalInput = document.getElementById('requestInterval');
    const updateButton = document.querySelector('button[onclick="updateInterval()"]');
    
    if (startBtn && stopBtn) {
        startBtn.disabled = state.isRunning;
        stopBtn.disabled = !state.isRunning;
    }
    
    if (intervalInput) {
        intervalInput.disabled = state.isRunning;
    }
    
    if (updateButton) {
        updateButton.disabled = state.isRunning;
    }
}

function showMessage(message, type = 'info') {
    const alertClass = type === 'error' ? 'alert-danger' : 
                      type === 'success' ? 'alert-success' : 
                      'alert-info';
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert ${alertClass} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('.container-fluid');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => alertDiv.remove(), 150);
    }, 3000);
}

// 状态刷新
async function refreshStatus() {
    try {
        const response = await fetch('/admin/collector/status');
        if (!response.ok) {
            throw new Error('获取状态失败');
        }
        
        const data = await response.json();
        console.log('收到的状态数据:', data);
        
        // 更新状态显示
        const statusBadge = document.getElementById('status-badge');
        if (statusBadge) {
            statusBadge.className = `badge text-bg-${data.is_running ? 'success' : 'danger'}`;
            statusBadge.style.color = '#000 !important';
            statusBadge.textContent = data.is_running ? '运行中' : '已停止';
        }

        // 更新采集间隔
        const intervalInput = document.getElementById('requestInterval');
        if (intervalInput && !intervalInput.matches(':focus')) {
            intervalInput.value = data.request_interval || 60;
        }

        // 更新其他状态信息
        document.getElementById('currentTaskId').textContent = data.current_task_id || '-';
        
        // 直接显示时间
        const lastTimeElement = document.getElementById('lastRequestTime');
        const nextTimeElement = document.getElementById('nextRequestTime');
        
        if (lastTimeElement) lastTimeElement.textContent = data.last_request_time;
        if (nextTimeElement) nextTimeElement.textContent = data.next_request_time;

        // 更新按钮状态
        state.isRunning = data.is_running;
        updateButtonsState();
    } catch (error) {
        console.error('刷新状态失败:', error);
    }
}

// 任务管理
async function createTask(event) {
    event.preventDefault();
    
    // 1. 添加输入验证
    const serverSelect = document.getElementById('serverSelect');
    if (!serverSelect.value) {
        showMessage('请选择服务器类型', 'error');
        return;
    }
    
    const selectedServer = parseInt(serverSelect.value);
    if (isNaN(selectedServer)) {
        showMessage('无效的服务器类型', 'error');
        return;
    }
    
    // 2. 获取并验证选中的商品
    const checkboxes = document.querySelectorAll('input[name="product_type"]:checked');
    if (checkboxes.length === 0) {
        showMessage('请至少选择一个商品类型', 'error');
        return;
    }
    
    // 3. 转换并验证商品ID
    const selectedProducts = [];
    for (const checkbox of checkboxes) {
        const productId = parseInt(checkbox.value);
        if (!isNaN(productId)) {
            selectedProducts.push(productId);
        }
    }
    
    if (selectedProducts.length === 0) {
        showMessage('没有有效的商品类型被选中', 'error');
        return;
    }
    
    // 4. 显示进度条
    const progressContainer = document.createElement('div');
    progressContainer.className = 'progress mt-3';
    progressContainer.innerHTML = `
        <div id="taskProgress" class="progress-bar" role="progressbar" 
             style="width: 0%" aria-valuenow="0" aria-valuemin="0" 
             aria-valuemax="100">0%</div>
    `;
    
    const form = document.getElementById('createTaskForm');
    form.appendChild(progressContainer);
    
    // 禁用提交按钮
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = '创建中...';
    
    // 5. 分批提交任务
    const BATCH_SIZE = 10;  // 每批处理10个任务
    const batches = [];
    for (let i = 0; i < selectedProducts.length; i += BATCH_SIZE) {
        const batch = selectedProducts.slice(i, i + BATCH_SIZE).map(product => ({
            server_type: selectedServer,
            product_type: product
        }));
        batches.push(batch);
    }
    
    const totalTasks = selectedProducts.length;
    let completedTasks = 0;
    let hasError = false;
    
    try {
        for (const batch of batches) {
            try {
                await submitTasks(batch);
                completedTasks += batch.length;
                showProgress(completedTasks, totalTasks);
            } catch (error) {
                hasError = true;
                showMessage(`批次处理失败: ${error.message}`, 'error');
            }
        }
        
        if (hasError) {
            showMessage('部分任务创建失败，请检查错误信息', 'warning');
        } else {
            showMessage('所有任务创建完成', 'success');
            setTimeout(() => location.reload(), 1000);
        }
    } catch (error) {
        showMessage(`任务创建失败: ${error.message}`, 'error');
    } finally {
        // 恢复提交按钮
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

// 显示进度
function showProgress(completed, total) {
    const progressBar = document.getElementById('taskProgress');
    if (progressBar) {
        const percentage = Math.round((completed / total) * 100);
        progressBar.style.width = `${percentage}%`;
        progressBar.textContent = `${percentage}%`;
    }
}

async function submitTasks(tasks) {
    const response = await fetch('/admin/task/batch_create', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ tasks: tasks })
    });

    const data = await response.json();
    if (data.status !== 'success') {
        throw new Error(data.message || '创建失败');
    }
    return data;
}

// 初始化商品选择区域
function initializeProducts() {
    const productList = document.getElementById('productList');
    
    GROUP_ORDER.forEach(groupName => {
        const productIds = PRODUCT_GROUPS[groupName];
        if (productIds && productIds.length > 0) {
            // 创建分组容器
            const groupContainer = document.createElement('div');
            groupContainer.className = 'product-group';
            groupContainer.id = `group-${groupName}`; // 添加锚点ID
            
            // 添加分组标题
            const groupTitle = document.createElement('div');
            groupTitle.className = 'product-group-title';
            groupTitle.textContent = groupName;
            groupContainer.appendChild(groupTitle);
            
            // 添加该分组的商品
            productIds.forEach(id => {
                const productName = PRODUCT_TYPES[id];
                if (productName) {
                    const checkbox = document.createElement('div');
                    checkbox.className = 'form-check';
                    checkbox.innerHTML = `
                        <input class="form-check-input" type="checkbox" 
                               name="product_type" value="${id}" 
                               id="product_${id}">
                        <label class="form-check-label" for="product_${id}">
                            ${productName} (${id})
                        </label>
                    `;
                    groupContainer.appendChild(checkbox);
                }
            });
            
            productList.appendChild(groupContainer);
        }
    });
}

// 修改全选/取消功能
function toggleAllProducts() {
    const checkboxes = document.querySelectorAll('input[name="product_type"]');
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    checkboxes.forEach(cb => cb.checked = !allChecked);
}

// 修改按分组选择功能
function selectProductGroup(groupName, productIds) {
    // 选中复选框
    const checkboxes = document.querySelectorAll('input[name="product_type"]');
    checkboxes.forEach(cb => {
        cb.checked = productIds.includes(parseInt(cb.value));
    });
    
    // 滚动到对应分组
    const groupElement = document.getElementById(`group-${groupName}`);
    if (groupElement) {
        groupElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// 任务删除
async function deleteTask(taskId) {
    if (!confirm('确定要删除这个任务吗？')) {
        return;
    }
    
    try {
        const response = await fetch('/admin/task/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: taskId })
        });

        const data = await response.json();
        if (data.status === 'success') {
            showMessage('任务删除成功', 'success');
            location.reload();
        } else {
            throw new Error(data.message || '删除失败');
        }
    } catch (error) {
        console.error('删除任务失败:', error);
        showMessage(error.message || '删除失败，请查看控制台获取详细信息', 'error');
    }
}

async function deleteAllTasks() {
    if (!confirm('确定要删除所有任务吗？此操作不可恢复！')) {
        return;
    }
    
    try {
        const response = await fetch('/admin/task/delete_all', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();
        if (data.status === 'success') {
            showMessage('所有任务已删除', 'success');
            location.reload();
        } else {
            throw new Error(data.message || '删除失败');
        }
    } catch (error) {
        console.error('删除所有任务失败:', error);
        showMessage(error.message || '删除失败，请查看控制台获取详细信息', 'error');
    }
}

// 更新采集间隔
async function updateInterval() {
    const interval = document.getElementById('requestInterval').value;
    if (!interval || interval < 1 || interval > 3600) {
        showMessage('请输入1-3600秒之间的数字', 'error');
        return;
    }
    
    try {
        const response = await fetch('/admin/collector/update_interval', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                request_interval: parseInt(interval)
            })
        });

        const data = await response.json();
        if (data.status === 'success') {
            showMessage('更新成功', 'success');
        } else {
            throw new Error(data.message || '更新失败');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage(error.message || '更新失败，请查看控制台获取详细信息', 'error');
    }
}

// 初始化商品选择器
function initProductSelect() {
    const productSelect = document.getElementById('productSelect');
    const { products, productGroups } = window.INITIAL_DATA;
    
    // 清空现有选项
    productSelect.innerHTML = '';
    
    // 按分组添加选项
    Object.entries(productGroups).forEach(([groupName, productIds]) => {
        const optgroup = document.createElement('optgroup');
        optgroup.label = groupName;
        
        productIds.forEach(productId => {
            if (products[productId]) {  // 确保商品存在
                const option = document.createElement('option');
                option.value = productId;
                option.textContent = `${products[productId]} (${productId})`;
                optgroup.appendChild(option);
            }
        });
        
        productSelect.appendChild(optgroup);
    });
}

// 初始化表格数据
function initializeTable() {
    const rows = document.querySelectorAll('#taskTableBody tr');
    allTasks = Array.from(rows);
    updatePagination();
    showCurrentPage();
}

// 更新分页信息
function updatePagination() {
    const totalPages = Math.ceil(allTasks.length / PAGE_SIZE);
    document.getElementById('currentPage').textContent = currentPage;
    document.getElementById('totalPages').textContent = totalPages;
}

// 显示当前页
function showCurrentPage() {
    const start = (currentPage - 1) * PAGE_SIZE;
    const end = start + PAGE_SIZE;
    
    // 隐藏所有行
    allTasks.forEach(row => row.style.display = 'none');
    
    // 显示当前页的行
    allTasks.slice(start, end).forEach(row => row.style.display = '');
    
    // 更新分页按钮状态
    const prevButton = document.querySelector('button[onclick="previousPage()"]');
    const nextButton = document.querySelector('button[onclick="nextPage()"]');
    
    prevButton.disabled = currentPage === 1;
    nextButton.disabled = currentPage === Math.ceil(allTasks.length / PAGE_SIZE);
}

// 上一页
function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        updatePagination();
        showCurrentPage();
    }
}

// 下一页
function nextPage() {
    const totalPages = Math.ceil(allTasks.length / PAGE_SIZE);
    if (currentPage < totalPages) {
        currentPage++;
        updatePagination();
        showCurrentPage();
    }
}

// 更新任务列表
async function updateTaskList() {
    try {
        const response = await fetch('/admin/collector/tasks');
        const result = await response.json();
        
        if (result.code === 0) {
            const { tasks, table_stats } = result.data;
            updateTableRows(tasks, table_stats);
        }
    } catch (error) {
        console.error('获取任务列表失败:', error);
    }
}

// 更新表格行
function updateTableRows(tasks, table_stats) {
    const tbody = document.querySelector('#taskTableBody');
    if (!tbody) return;
    
    tasks.forEach(task => {
        const tableName = `market_${task.server_type}_${task.product_type}`;
        const stats = table_stats[tableName] || {
            total_count: 0,
            batch_count: 0,
            last_batch_count: 0,
            last_update_time: '-'
        };
        
        // 查找现有行
        const existingRow = tbody.querySelector(`tr[data-task-id="${task.id}"]`);
        if (existingRow) {
            // 更新最后更新时间
            const lastTimeCell = existingRow.querySelector('.last-time');
            if (lastTimeCell) {
                lastTimeCell.textContent = stats.last_update_time || '-';
            }
            
            // 更新最新批次数据量
            const countCell = existingRow.querySelector('.collection-count');
            if (countCell) {
                countCell.textContent = stats.last_batch_count || 0;
            }
            
            // 更新采集状态
            const statusCell = existingRow.querySelector('.collection-status');
            if (statusCell) {
                statusCell.innerHTML = `<span class="badge text-bg-${task.last_collection_success ? 'success' : 'danger'}">${task.last_collection_success ? '成功' : '失败'}</span>`;
                if (!task.last_collection_success && task.last_error) {
                    statusCell.title = task.last_error;
                }
            }
            
            // 更新总采集次数
            const totalCell = existingRow.querySelector('.total-collections');
            if (totalCell) {
                totalCell.textContent = stats.batch_count || 0;
            }
            
            // 更新实际记录数
            const recordCell = existingRow.querySelector('.record-count');
            if (recordCell) {
                recordCell.textContent = stats.total_count || 0;
            }
        }
    });
} 