/* Логика для Telegram-страницы */
document.addEventListener('DOMContentLoaded', function () {
    // Элементы DOM
    const form = document.getElementById('telegram-form');
    const loader = document.getElementById('loader');
    const cardContent = document.getElementById('card-content');
    const audio = document.getElementById('loading-audio');
    const volumeToggle = document.getElementById('volume-toggle');
    const postRows = document.querySelectorAll('.post-row');
    const postDetails = document.getElementById('post-details');
    const reactionsList = document.getElementById('reactions-list');
    const reactionsToggle = document.getElementById('reactions-toggle');
    const commentsList = document.getElementById('comments-list');
    const commentsPagination = document.getElementById('comments-pagination');
    const closeDetails = document.getElementById('close-details');
    const tableContainer = document.getElementById('table-container');
    const detailViews = document.getElementById('detail-views');
    const detailForwards = document.getElementById('detail-forwards');
    const detailReactions = document.getElementById('detail-reactions');
    const detailComments = document.getElementById('detail-comments');
    const applyChangesBtn = document.getElementById('apply-changes-btn');
    const resetChangesBtn = document.getElementById('reset-changes-btn');

    // Переменные состояния
    let enableLoader = false;
    let currentPostId = null;
    let currentChannelId = null;
    let currentPage = 1;
    const commentsPerPage = 10;
    let hasChanges = false;
    let categoryChanges = JSON.parse(localStorage.getItem('categoryChanges')) || {};

    // Функция получения CSRF-токена
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Проверка изменений в категориях
    function checkForChanges() {
        hasChanges = false;
        postRows.forEach(row => {
            const postId = row.getAttribute('data-post-id');
            const originalCategory = row.getAttribute('data-original-category');
            if (categoryChanges[postId] && categoryChanges[postId] !== originalCategory) {
                hasChanges = true;
            }
        });
        applyChangesBtn.disabled = !hasChanges;
        resetChangesBtn.style.display = hasChanges ? 'block' : 'none';
    }

    // Загрузка деталей поста
    async function loadPostDetails(postId, channelId, page = 1) {
        currentPostId = postId;
        currentChannelId = channelId;
        currentPage = page;

        try {
            const response = await fetch(`/get_post_details/?post_id=${postId}&channel_id=${channelId}&page=${page}&limit=${commentsPerPage}`);
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! Status: ${response.status}, Message: ${errorText}`);
            }
            const data = await response.json();

            const row = Array.from(postRows).find(row => row.getAttribute('data-post-id') === postId);
            detailViews.textContent = row.getAttribute('data-views') || 'N/A';
            detailForwards.textContent = row.getAttribute('data-forwards') || 'N/A';
            detailReactions.textContent = row.getAttribute('data-reactions') || '0';
            detailComments.textContent = row.getAttribute('data-comments') || '0';

            reactionsList.innerHTML = '';
            reactionsToggle.innerHTML = '';
            commentsList.innerHTML = '';
            const paginationUl = commentsPagination.querySelector('ul');
            paginationUl.innerHTML = '';

            if (data.reactions && data.reactions.length > 0) {
                const visibleReactions = data.reactions.slice(0, 3);
                const hiddenReactions = data.reactions.slice(3);

                visibleReactions.forEach(reaction => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item reaction-item';
                    const emoticon = reaction.emoticon.startsWith('custom_') ? '[Кастомная реакция]' : reaction.emoticon;
                    li.innerHTML = `<span class="reaction-emoji">${emoticon}</span> - ${reaction.count} ${reaction.count === 1 ? 'человек' : 'человек'}`;
                    reactionsList.appendChild(li);
                });

                if (hiddenReactions.length > 0) {
                    const hiddenContainer = document.createElement('div');
                    hiddenContainer.className = 'hidden-reactions';
                    hiddenContainer.style.display = 'none';
                    hiddenReactions.forEach(reaction => {
                        const li = document.createElement('li');
                        li.className = 'list-group-item reaction-item';
                        const emoticon = reaction.emoticon.startsWith('custom_') ? '[Кастомная реакция]' : reaction.emoticon;
                        li.innerHTML = `<span class="reaction-emoji">${emoticon}</span> - ${reaction.count} ${reaction.count === 1 ? 'человек' : 'человек'}`;
                        hiddenContainer.appendChild(li);
                    });
                    reactionsList.appendChild(hiddenContainer);

                    const toggleLink = document.createElement('a');
                    toggleLink.href = '#';
                    toggleLink.className = 'toggle-reactions';
                    toggleLink.textContent = 'развернуть';
                    reactionsToggle.appendChild(toggleLink);

                    reactionsToggle.style.display = 'block';
                    toggleLink.addEventListener('click', function (e) {
                        e.preventDefault();
                        if (hiddenContainer.style.display === 'none') {
                            hiddenContainer.style.display = 'block';
                            this.textContent = 'свернуть';
                        } else {
                            hiddenContainer.style.display = 'none';
                            this.textContent = 'развернуть';
                        }
                    });
                } else {
                    reactionsToggle.style.display = 'none';
                }
            } else {
                reactionsList.innerHTML = '<li class="list-group-item">Нет реакций</li>';
                reactionsToggle.style.display = 'none';
            }

            if (data.total_comments > 0 && data.comments && data.comments.length > 0) {
                data.comments.forEach(comment => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item';

                    const message = comment.message || '[Без текста]';
                    const isLongMessage = message.length > 100;
                    const shortMessage = isLongMessage ? message.slice(0, 100) + '...' : message;
                    const fullMessage = message;

                    const messageContainer = document.createElement('div');
                    messageContainer.className = 'comment-message';

                    const shortText = document.createElement('p');
                    shortText.className = 'mb-1 short-comment';
                    shortText.textContent = shortMessage;
                    messageContainer.appendChild(shortText);

                    const fullText = document.createElement('p');
                    fullText.className = 'mb-1 full-comment';
                    fullText.textContent = fullMessage;
                    fullText.style.display = 'none';
                    messageContainer.appendChild(fullText);

                    if (isLongMessage) {
                        const toggleLink = document.createElement('a');
                        toggleLink.href = '#';
                        toggleLink.className = 'toggle-comment';
                        toggleLink.textContent = 'читать далее';
                        messageContainer.appendChild(toggleLink);

                        toggleLink.addEventListener('click', function (e) {
                            e.preventDefault();
                            if (shortText.style.display === 'none') {
                                shortText.style.display = 'block';
                                fullText.style.display = 'none';
                                this.textContent = 'читать далее';
                            } else {
                                shortText.style.display = 'none';
                                fullText.style.display = 'block';
                                this.textContent = 'свернуть';
                            }
                        });
                    }

                    li.appendChild(messageContainer);

                    const meta = document.createElement('small');
                    meta.className = 'text-muted';
                    meta.innerHTML = `
                        Автор: ${comment.author || 'Аноним'} | 
                        Дата: ${comment.date} | 
                        Репостов: ${comment.forwards} | 
                        Ответов: ${comment.replies}
                    `;
                    li.appendChild(meta);

                    commentsList.appendChild(li);
                });
            } else {
                commentsList.innerHTML = '<li class="list-group-item">Комментарии отсутствуют или запрещены в этом канале</li>';
            }

            const totalComments = data.total_comments || 0;
            const totalPages = Math.ceil(totalComments / commentsPerPage);
            if (totalPages > 1) {
                if (page > 1) {
                    const prevLi = document.createElement('li');
                    prevLi.className = 'page-item';
                    prevLi.innerHTML = `<a class="page-link" href="#" data-page="${page - 1}">«</a>`;
                    paginationUl.appendChild(prevLi);
                }
                for (let i = 1; i <= totalPages; i++) {
                    const li = document.createElement('li');
                    li.className = `page-item ${i === page ? 'active' : ''}`;
                    li.innerHTML = `<a class="page-link" href="#" data-page="${i}">${i}</a>`;
                    paginationUl.appendChild(li);
                }
                if (page < totalPages) {
                    const nextLi = document.createElement('li');
                    nextLi.className = 'page-item';
                    nextLi.innerHTML = `<a class="page-link" href="#" data-page="${page + 1}">»</a>`;
                    paginationUl.appendChild(nextLi);
                }
            }

            highlightActivePost();
        } catch (error) {
            console.error('Error loading post details:', error);
            commentsList.innerHTML = `<li class="list-group-item">Ошибка загрузки комментариев: ${error.message}</li>`;
        }
    }

    // Подсветка активного поста
    function highlightActivePost() {
        postRows.forEach(row => {
            row.classList.remove('active-post');
            if (row.getAttribute('data-post-id') === currentPostId) {
                row.classList.add('active-post');
            }
        });
    }

    // Закрытие деталей поста
    function closePostDetails() {
        postDetails.style.display = 'none';
        tableContainer.classList.remove('shrunk');
        postRows.forEach(row => row.classList.remove('active-post'));
        currentPostId = null;
    }

    // Обработчики событий
    volumeToggle.addEventListener('click', function () {
        enableLoader = !enableLoader;
        if (enableLoader) {
            volumeToggle.classList.remove('fa-volume-mute');
            volumeToggle.classList.add('fa-volume-down');
            audio.muted = false;
            volumeToggle.classList.remove('fa-volume-mute');
            volumeToggle.classList.add('fa-volume-up');
        } else {
            volumeToggle.classList.remove('fa-volume-down');
            volumeToggle.classList.add('fa-volume-mute');
            audio.muted = true;
            volumeToggle.classList.remove('fa-volume-up');
            volumeToggle.classList.add('fa-volume-mute');
        }
    });

    form.addEventListener('submit', function () {
        if (enableLoader) {
            cardContent.style.display = 'none';
            loader.style.display = 'block';
            audio.play();
        } else {
            cardContent.style.display = 'block';
            loader.style.display = 'none';
            audio.pause();
        }
    });

    postRows.forEach(row => {
        row.addEventListener('click', async function (e) {
            const target = e.target;
            if (target && target.classList && (target.classList.contains('read-more') || target.tagName === 'SELECT')) {
                return;
            }
            const postId = this.getAttribute('data-post-id');
            const channelId = this.getAttribute('data-channel-id');
            if (!postId || !channelId) {
                return;
            }

            if (this.classList.contains('active-post')) {
                closePostDetails();
            } else {
                postRows.forEach(r => r.classList.remove('active-post'));
                this.classList.add('active-post');
                postDetails.style.display = 'block';
                tableContainer.classList.add('shrunk');
                await loadPostDetails(postId, channelId, 1);
            }
        });
    });

    closeDetails.addEventListener('click', closePostDetails);

    commentsPagination.addEventListener('click', async function (e) {
        e.preventDefault();
        const target = e.target.closest('a');
        if (target) {
            const page = parseInt(target.getAttribute('data-page'));
            if (page) {
                await loadPostDetails(currentPostId, currentChannelId, page);
            }
        }
    });

    document.addEventListener('click', function (e) {
        const target = e.target;
        if (target && target.classList && target.classList.contains('read-more')) {
            e.preventDefault();
            e.stopPropagation();
            const parentTd = target.parentElement;
            const shortText = parentTd.querySelector('.post-text-short');
            const fullText = parentTd.querySelector('.post-text-full');
            const isExpanded = target.getAttribute('data-expanded') === 'true';

            if (!isExpanded) {
                shortText.style.display = 'none';
                fullText.style.display = 'inline';
                target.textContent = 'свернуть';
                target.setAttribute('data-expanded', 'true');
                parentTd.removeChild(target);
                parentTd.appendChild(target);
            } else {
                shortText.style.display = 'inline';
                fullText.style.display = 'none';
                target.textContent = 'читать далее';
                target.setAttribute('data-expanded', 'false');
                parentTd.removeChild(target);
                shortText.insertAdjacentElement('afterend', target);
            }
        }
    });

    const filterAll = document.getElementById('filter-all');
    const filterCheckboxes = document.querySelectorAll('input[name="filter"]:not(#filter-all)');
    if (filterAll) {
        filterAll.addEventListener('change', function () {
            if (this.checked) {
                filterCheckboxes.forEach(checkbox => {
                    checkbox.checked = false;
                });
            }
        });

        filterCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function () {
                if (this.checked) {
                    filterAll.checked = false;
                }
            });
        });
    }

    const categoryFilterAll = document.getElementById('category-filter-all');
    const categoryCheckboxes = document.querySelectorAll('input[name="category_filter"]:not(#category-filter-all)');
    if (categoryFilterAll) {
        categoryFilterAll.addEventListener('change', function () {
            if (this.checked) {
                categoryCheckboxes.forEach(checkbox => {
                    checkbox.checked = false;
                });
            }
        });

        categoryCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function () {
                if (this.checked) {
                    categoryFilterAll.checked = false;
                }
            });
        });
    }

    document.querySelectorAll('.category-select').forEach(select => {
        const postId = select.getAttribute('data-post-id');
        if (categoryChanges[postId]) {
            select.value = categoryChanges[postId];
            const row = select.closest('tr');
            row.classList.add('modified');
        }
    });

    document.querySelectorAll('.category-select').forEach(select => {
        select.addEventListener('change', function () {
            const category = this.value;
            const postId = this.getAttribute('data-post-id');
            const row = this.closest('tr');
            const originalCategory = row.getAttribute('data-original-category');

            categoryChanges[postId] = category;
            localStorage.setItem('categoryChanges', JSON.stringify(categoryChanges));

            if (category !== originalCategory) {
                row.classList.add('modified');
                hasChanges = true;
                applyChangesBtn.disabled = false;
                resetChangesBtn.style.display = 'block';
            } else {
                row.classList.remove('modified');
                delete categoryChanges[postId];
                localStorage.setItem('categoryChanges', JSON.stringify(categoryChanges));
                checkForChanges();
            }
        });
    });

    applyChangesBtn.addEventListener('click', async function () {
        if (!hasChanges) {
            alert('Нет изменений для применения.');
            return;
        }

        const dataId = this.getAttribute('data-data-id');
        const button = this;
        button.disabled = true;
        button.textContent = 'Обучение модели...';

        const formData = new FormData();
        formData.append('data_id', dataId);
        formData.append('changes', JSON.stringify(categoryChanges));

        try {
            const response = await fetch('/apply_changes/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: formData
            });
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! Status: ${response.status}, Message: ${errorText}`);
            }
            const result = await response.json();

            if (result.success) {
                document.querySelectorAll('tr.modified').forEach(row => {
                    row.classList.remove('modified');
                    const select = row.querySelector('.category-select');
                    row.setAttribute('data-original-category', select.value);
                });
                hasChanges = false;
                button.disabled = true;
                resetChangesBtn.style.display = 'none';
                localStorage.removeItem('categoryChanges');
                categoryChanges = {};
                alert('Модель успешно переобучена!');
            } else {
                alert('Ошибка: ' + result.error);
            }
        } catch (error) {
            console.error('Error applying changes:', error);
            alert('Ошибка при переобучении модели: ' + error.message);
        } finally {
            button.textContent = 'Применить';
        }
    });

    resetChangesBtn.addEventListener('click', function () {
        if (!hasChanges) {
            alert('Нет изменений для отмены.');
            return;
        }

        categoryChanges = {};
        localStorage.removeItem('categoryChanges');
        document.querySelectorAll('tr.modified').forEach(row => {
            row.classList.remove('modified');
            const select = row.querySelector('.category-select');
            select.value = row.getAttribute('data-original-category');
        });
        hasChanges = false;
        applyChangesBtn.disabled = true;
        resetChangesBtn.style.display = 'none';
        alert('Изменения отменены.');
    });

    document.querySelectorAll('.pagination-link').forEach(link => {
        link.addEventListener('click', function (e) {
            localStorage.setItem('categoryChanges', JSON.stringify(categoryChanges));
        });
    });
});