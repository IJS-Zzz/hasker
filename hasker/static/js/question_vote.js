function getCookie(name) {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}

$(function() {
    $('a.vote').click(function (event) {
        event.preventDefault();
        let url = $(this).attr('href');
        let $rating = $(this).parent().find('.rating');
        $.post(url, {
            'value': $(this).hasClass('vote-up'),
            'csrfmiddlewaretoken': getCookie('csrftoken')
        }, function (response) {
            $rating.text(response['rating']);
        });
    }
    );

    $('a.answer-mark').click(function (event) {
        event.preventDefault();
        let $this = $(this);
        let url = $this.attr('href');
        $.post(url, {
            'csrfmiddlewaretoken': getCookie('csrftoken')
        }, function (response) {
            if (response['success']) {
                let $star = $this.find('.answer-mark-star');
                let needActivate = !$star.hasClass('fas');
                $('.answer-list').find('.answer-mark-star').each(function () {
                    console.log(this);
                    $(this).removeClass('fas');
                    $(this).addClass('far');
                });
                if (needActivate) {
                    $star.removeClass('far');
                    $star.addClass('fas');
                }
            }

        });
    });
});