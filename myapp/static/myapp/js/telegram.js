document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('telegram-form');
    var loader = document.getElementById('loader');
    var cardContent = document.getElementById('card-content');
    var audio = document.getElementById('loading-audio');
    var volumeToggle = document.getElementById('volume-toggle');
    var enableLoader = false;

    volumeToggle.addEventListener('click', function() {
        enableLoader = !enableLoader;
        if (enableLoader) {
            volumeToggle.classList.remove('fa-volume-mute');
            volumeToggle.classList.add('fa-volume-down');
        } else {
            volumeToggle.classList.remove('fa-volume-down');
            volumeToggle.classList.add('fa-volume-mute');
        }
    });

    form.addEventListener('submit', function() {
        if (enableLoader) {
            cardContent.style.display = 'none';  // Скрываем содержимое карточки
            loader.style.display = 'block';  // Показываем GIF-анимацию
            audio.play();  // Воспроизводим аудио
        } else {
            cardContent.style.display = 'block';  // Показываем содержимое карточки
            loader.style.display = 'none';  // Скрываем GIF-анимацию
            audio.pause();  // Останавливаем аудио
        }
    });

    var readMoreLinks = document.querySelectorAll('.read-more');
    readMoreLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            var shortText = this.previousElementSibling.previousElementSibling;
            var fullText = this.previousElementSibling;
            if (fullText.style.display === 'none') {
                fullText.style.display = 'inline';
                shortText.style.display = 'none';
                this.textContent = 'скрыть';
            } else {
                fullText.style.display = 'none';
                shortText.style.display = 'inline';
                this.textContent = 'читать далее';
            }
        });
    });

    // Управление поведением чекбоксов
    var filterAll = document.getElementById('filter-all');
    var filterCheckboxes = document.querySelectorAll('input[name="filter"]');

    filterAll.addEventListener('change', function() {
        if (this.checked) {
            filterCheckboxes.forEach(function(checkbox) {
                if (checkbox !== filterAll) {
                    checkbox.checked = false;
                }
            });
        }
    });

    filterCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            if (this !== filterAll && this.checked) {
                filterAll.checked = false;
            }
        });
    });
});