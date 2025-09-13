// Vue.js приложение для Postopus Web Interface

const { createApp } = Vue;

createApp({
    data() {
        return {
            // Текущий вид
            currentView: 'dashboard',
            
            // Данные дашборда
            stats: {
                total_posts: 0,
                published_today: 0,
                scheduled_tasks: 0,
                error_count: 0
            },
            recentPosts: [],
            chartData: null,
            
            // Данные постов
            posts: [],
            postFilters: {
                status: '',
                platform: '',
                search: ''
            },
            
            // Данные планировщика
            tasks: [],
            schedulerStatus: {
                tasks: { total: 0, enabled: 0, running: 0 },
                executions: { today: 0, successful: 0, failed: 0 }
            },
            
            // Настройки
            settings: {
                text_post_maxsize_simbols: 4000,
                table_size: 30
            },
            settingsTab: 'general',
            vkTokens: '',
            vkPostTokens: '',
            telegramBotToken: '',
            telegramChatId: '',
            blacklistText: '',
            blackIdText: '',
            
            // Модальные окна
            showCreatePostModal: false,
            showCreateTaskModal: false,
            
            // Новые объекты
            newPost: {
                text: '',
                target_platforms: ['vk'],
                scheduled_at: ''
            },
            newTask: {
                name: '',
                description: '',
                schedule: '',
                session_name: 'novost'
            },
            
            // Состояние загрузки
            loading: false,
            
            // API базовый URL
            apiBaseUrl: '/api'
        }
    },
    
    mounted() {
        this.initializeApp();
    },
    
    methods: {
        // Инициализация приложения
        async initializeApp() {
            try {
                await this.loadDashboardData();
                await this.loadSchedulerStatus();
                this.setupChart();
            } catch (error) {
                console.error('Error initializing app:', error);
                this.showAlert('Ошибка инициализации приложения', 'danger');
            }
        },
        
        // Загрузка данных дашборда
        async loadDashboardData() {
            try {
                this.loading = true;
                
                // Загружаем статистику
                const statsResponse = await axios.get(`${this.apiBaseUrl}/dashboard/stats`);
                this.stats = statsResponse.data;
                
                // Загружаем недавние посты
                const postsResponse = await axios.get(`${this.apiBaseUrl}/dashboard/recent-posts`);
                this.recentPosts = postsResponse.data;
                
                // Загружаем данные для графика
                const chartResponse = await axios.get(`${this.apiBaseUrl}/dashboard/chart-data`);
                this.chartData = chartResponse.data;
                
                // Обновляем график
                this.updateChart();
                
            } catch (error) {
                console.error('Error loading dashboard data:', error);
                this.showAlert('Ошибка загрузки данных дашборда', 'danger');
            } finally {
                this.loading = false;
            }
        },
        
        // Загрузка постов
        async loadPosts() {
            try {
                this.loading = true;
                
                const params = new URLSearchParams();
                if (this.postFilters.status) params.append('status', this.postFilters.status);
                if (this.postFilters.platform) params.append('platform', this.postFilters.platform);
                
                const response = await axios.get(`${this.apiBaseUrl}/posts?${params}`);
                this.posts = response.data;
                
            } catch (error) {
                console.error('Error loading posts:', error);
                this.showAlert('Ошибка загрузки постов', 'danger');
            } finally {
                this.loading = false;
            }
        },
        
        // Загрузка задач
        async loadTasks() {
            try {
                this.loading = true;
                
                const response = await axios.get(`${this.apiBaseUrl}/scheduler/tasks`);
                this.tasks = response.data;
                
            } catch (error) {
                console.error('Error loading tasks:', error);
                this.showAlert('Ошибка загрузки задач', 'danger');
            } finally {
                this.loading = false;
            }
        },
        
        // Загрузка статуса планировщика
        async loadSchedulerStatus() {
            try {
                const response = await axios.get(`${this.apiBaseUrl}/scheduler/status`);
                this.schedulerStatus = response.data;
                
            } catch (error) {
                console.error('Error loading scheduler status:', error);
            }
        },
        
        // Создание поста
        async createPost() {
            try {
                this.loading = true;
                
                const postData = {
                    text: this.newPost.text,
                    target_platforms: this.newPost.target_platforms,
                    scheduled_at: this.newPost.scheduled_at || null
                };
                
                await axios.post(`${this.apiBaseUrl}/posts`, postData);
                
                this.showCreatePostModal = false;
                this.resetNewPost();
                this.showAlert('Пост создан успешно', 'success');
                
                // Перезагружаем посты если мы на странице постов
                if (this.currentView === 'posts') {
                    await this.loadPosts();
                }
                
            } catch (error) {
                console.error('Error creating post:', error);
                this.showAlert('Ошибка создания поста', 'danger');
            } finally {
                this.loading = false;
            }
        },
        
        // Публикация поста
        async publishPost(postId) {
            try {
                this.loading = true;
                
                await axios.post(`${this.apiBaseUrl}/posts/${postId}/publish`);
                
                this.showAlert('Пост поставлен в очередь на публикацию', 'success');
                await this.loadPosts();
                
            } catch (error) {
                console.error('Error publishing post:', error);
                this.showAlert('Ошибка публикации поста', 'danger');
            } finally {
                this.loading = false;
            }
        },
        
        // Удаление поста
        async deletePost(postId) {
            if (!confirm('Вы уверены, что хотите удалить этот пост?')) {
                return;
            }
            
            try {
                this.loading = true;
                
                await axios.delete(`${this.apiBaseUrl}/posts/${postId}`);
                
                this.showAlert('Пост удален успешно', 'success');
                await this.loadPosts();
                
            } catch (error) {
                console.error('Error deleting post:', error);
                this.showAlert('Ошибка удаления поста', 'danger');
            } finally {
                this.loading = false;
            }
        },
        
        // Создание задачи
        async createTask() {
            try {
                this.loading = true;
                
                const taskData = {
                    name: this.newTask.name,
                    description: this.newTask.description,
                    schedule: this.newTask.schedule,
                    session_name: this.newTask.session_name
                };
                
                await axios.post(`${this.apiBaseUrl}/scheduler/tasks`, taskData);
                
                this.showCreateTaskModal = false;
                this.resetNewTask();
                this.showAlert('Задача создана успешно', 'success');
                
                // Перезагружаем задачи если мы на странице планировщика
                if (this.currentView === 'scheduler') {
                    await this.loadTasks();
                }
                
            } catch (error) {
                console.error('Error creating task:', error);
                this.showAlert('Ошибка создания задачи', 'danger');
            } finally {
                this.loading = false;
            }
        },
        
        // Запуск задачи
        async runTask(taskId) {
            try {
                this.loading = true;
                
                await axios.post(`${this.apiBaseUrl}/scheduler/tasks/${taskId}/run`);
                
                this.showAlert('Задача поставлена в очередь на выполнение', 'success');
                await this.loadTasks();
                
            } catch (error) {
                console.error('Error running task:', error);
                this.showAlert('Ошибка запуска задачи', 'danger');
            } finally {
                this.loading = false;
            }
        },
        
        // Переключение статуса задачи
        async toggleTask(taskId, enabled) {
            try {
                this.loading = true;
                
                await axios.put(`${this.apiBaseUrl}/scheduler/tasks/${taskId}`, {
                    enabled: enabled
                });
                
                this.showAlert(`Задача ${enabled ? 'включена' : 'отключена'}`, 'success');
                await this.loadTasks();
                
            } catch (error) {
                console.error('Error toggling task:', error);
                this.showAlert('Ошибка изменения статуса задачи', 'danger');
            } finally {
                this.loading = false;
            }
        },
        
        // Удаление задачи
        async deleteTask(taskId) {
            if (!confirm('Вы уверены, что хотите удалить эту задачу?')) {
                return;
            }
            
            try {
                this.loading = true;
                
                await axios.delete(`${this.apiBaseUrl}/scheduler/tasks/${taskId}`);
                
                this.showAlert('Задача удалена успешно', 'success');
                await this.loadTasks();
                
            } catch (error) {
                console.error('Error deleting task:', error);
                this.showAlert('Ошибка удаления задачи', 'danger');
            } finally {
                this.loading = false;
            }
        },
        
        // Сохранение общих настроек
        async saveGeneralSettings() {
            try {
                this.loading = true;
                
                await axios.put(`${this.apiBaseUrl}/settings/general`, this.settings);
                
                this.showAlert('Настройки сохранены успешно', 'success');
                
            } catch (error) {
                console.error('Error saving general settings:', error);
                this.showAlert('Ошибка сохранения настроек', 'danger');
            } finally {
                this.loading = false;
            }
        },
        
        // Сохранение настроек VK
        async saveVKSettings() {
            try {
                this.loading = true;
                
                const vkConfig = {
                    tokens: this.vkTokens.split(',').map(t => t.trim()).filter(t => t),
                    read_tokens: this.vkTokens.split(',').map(t => t.trim()).filter(t => t),
                    post_tokens: this.vkPostTokens.split(',').map(t => t.trim()).filter(t => t),
                    repost_tokens: this.vkPostTokens.split(',').map(t => t.trim()).filter(t => t)
                };
                
                await axios.put(`${this.apiBaseUrl}/settings/vk`, vkConfig);
                
                this.showAlert('Настройки VK сохранены успешно', 'success');
                
            } catch (error) {
                console.error('Error saving VK settings:', error);
                this.showAlert('Ошибка сохранения настроек VK', 'danger');
            } finally {
                this.loading = false;
            }
        },
        
        // Сохранение настроек Telegram
        async saveTelegramSettings() {
            try {
                this.loading = true;
                
                const telegramConfig = {
                    bot_token: this.telegramBotToken,
                    chat_id: this.telegramChatId
                };
                
                await axios.put(`${this.apiBaseUrl}/settings/telegram`, telegramConfig);
                
                this.showAlert('Настройки Telegram сохранены успешно', 'success');
                
            } catch (error) {
                console.error('Error saving Telegram settings:', error);
                this.showAlert('Ошибка сохранения настроек Telegram', 'danger');
            } finally {
                this.loading = false;
            }
        },
        
        // Сохранение настроек фильтров
        async saveFilterSettings() {
            try {
                this.loading = true;
                
                const filterConfig = {
                    delete_msg_blacklist: this.blacklistText.split('\n').map(t => t.trim()).filter(t => t),
                    black_id: this.blackIdText.split(',').map(t => parseInt(t.trim())).filter(t => !isNaN(t))
                };
                
                await axios.put(`${this.apiBaseUrl}/settings/filters`, filterConfig);
                
                this.showAlert('Настройки фильтров сохранены успешно', 'success');
                
            } catch (error) {
                console.error('Error saving filter settings:', error);
                this.showAlert('Ошибка сохранения настроек фильтров', 'danger');
            } finally {
                this.loading = false;
            }
        },
        
        // Тестирование подключения
        async testConnection(platform) {
            try {
                this.loading = true;
                
                const response = await axios.post(`${this.apiBaseUrl}/settings/test-connection`, {
                    platform: platform
                });
                
                this.showAlert(response.data.message, 'success');
                
            } catch (error) {
                console.error('Error testing connection:', error);
                this.showAlert('Ошибка тестирования подключения', 'danger');
            } finally {
                this.loading = false;
            }
        },
        
        // Настройка графика
        setupChart() {
            const ctx = document.getElementById('postsChart');
            if (ctx) {
                this.chart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: []
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        },
                        plugins: {
                            legend: {
                                position: 'top',
                            }
                        }
                    }
                });
            }
        },
        
        // Обновление графика
        updateChart() {
            if (this.chart && this.chartData) {
                this.chart.data.labels = this.chartData.labels;
                this.chart.data.datasets = this.chartData.datasets;
                this.chart.update();
            }
        },
        
        // Сброс формы нового поста
        resetNewPost() {
            this.newPost = {
                text: '',
                target_platforms: ['vk'],
                scheduled_at: ''
            };
        },
        
        // Сброс формы новой задачи
        resetNewTask() {
            this.newTask = {
                name: '',
                description: '',
                schedule: '',
                session_name: 'novost'
            };
        },
        
        // Форматирование даты
        formatDate(dateString) {
            if (!dateString) return 'Не указано';
            
            const date = new Date(dateString);
            return date.toLocaleString('ru-RU', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        
        // Показ уведомления
        showAlert(message, type = 'info') {
            // Создаем элемент уведомления
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
            alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            // Добавляем в DOM
            document.body.appendChild(alertDiv);
            
            // Автоматически удаляем через 5 секунд
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.parentNode.removeChild(alertDiv);
                }
            }, 5000);
        },
        
        // Выход из системы
        logout() {
            if (confirm('Вы уверены, что хотите выйти из системы?')) {
                // Здесь должна быть логика выхода
                window.location.href = '/login';
            }
        },
        
        // Обработка изменения вида
        async onViewChange(view) {
            this.currentView = view;
            
            // Загружаем данные в зависимости от вида
            switch (view) {
                case 'posts':
                    await this.loadPosts();
                    break;
                case 'scheduler':
                    await this.loadTasks();
                    break;
                case 'dashboard':
                    await this.loadDashboardData();
                    break;
            }
        }
    },
    
    watch: {
        currentView(newView) {
            this.onViewChange(newView);
        }
    }
}).mount('#app');
