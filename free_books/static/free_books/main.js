// http://stackoverflow.com/a/1714899/895245
var urlencode = function(obj) {
    var str = [];
    for (var p in obj) {
        if (obj.hasOwnProperty(p)) {
            str.push(encodeURIComponent(p) + '=' + encodeURIComponent(obj[p]));
        }
    }
    return str.join('&');
}

window.onload = function() {
    var view = document.body.getAttribute('data-view');
    if (view === 'article_detail') {
        var elements = document.querySelectorAll('.vote');
        for (var i = 0; i < elements.length; i++) {
            elements[i].addEventListener(
                'click',
                function(e) {
                    e.preventDefault();
                    var x = new XMLHttpRequest();
                    x.open('POST', e.target.getAttribute('href'), true);
                    x.setRequestHeader('X-CSRFToken', Cookies.get('csrftoken'))
                    x.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded;charset=utf-8')
                    x.onreadystatechange = function() {
                        if (x.readyState == 4 && x.status == 200) {
                            alert('OK')
                        }
                    }
                    x.send(urlencode(e.target.dataset));
                },
                false
            );
        }
    }
};
