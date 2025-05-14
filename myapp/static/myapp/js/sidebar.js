/* Логика для сайдбара и hamburger-меню */
jQuery(document).ready(function ($) {
    const trigger = $('.hamburger');
    const overlay = $('.overlay');
    let isClosed = false;

    // Обработчик клика по hamburger-меню
    trigger.click(function () {
        hamburgerCross();
    });

    // Функция для переключения состояния hamburger-меню
    function hamburgerCross() {
        if (isClosed) {
            overlay.hide();
            trigger.removeClass('is-open').addClass('is-closed');
            isClosed = false;
        } else {
            overlay.show();
            trigger.removeClass('is-closed').addClass('is-open');
            isClosed = true;
        }
    }

    // Переключение класса toggled для wrapper
    $('[data-toggle="offcanvas"]').click(function () {
        $('#wrapper').toggleClass('toggled');
    });
});