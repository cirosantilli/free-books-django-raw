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

var incrementElem = function(elem, delta) {
    elem.innerHTML = parseInt(elem.innerHTML) + delta;
}

window.onload = function() {
    var view = document.body.getAttribute('data-view');
    if (view === 'article_detail') {
        // Send request to server.
        var elements = document.querySelectorAll('.vote');
        for (var i = 0; i < elements.length; i++) {
            elements[i].addEventListener(
                'click',
                function(e) {
                    e.preventDefault();
                    var x = new XMLHttpRequest();
                    // TODO required, why? Otherwise e.currentTarget is null inside the XHR.
                    var currentTarget = e.currentTarget;
                    x.open('POST', currentTarget.getAttribute('href'), true);
                    x.setRequestHeader('X-CSRFToken', Cookies.get('csrftoken'));
                    x.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded;charset=utf-8');
                    x.onreadystatechange = function() {
                        if (x.readyState == 4) {
                            if (x.status != 200) {
                                // TODO translate this.
                                alert('Action failed.');
                            }
                        }
                    }
                    x.send(urlencode(currentTarget.dataset));
                },
                false
            );
        }

        // Optimistically update the UI locally.
        var upvote_count_elem = document.getElementById('upvote-count');
        var upvote_onoff_elem = document.getElementById('upvote-onoff');
        var downvote_count_elem = document.getElementById('downvote-count');
        var downvote_onoff_elem = document.getElementById('downvote-onoff');
        var net_votes_elem = document.getElementById('net-votes');
        var has_upvote = document.querySelectorAll('#upvote-onoff.on #upvote').length === 0;
        var has_downvote = document.querySelectorAll('#downvote-onoff.on #downvote').length === 0;
        document.getElementById('upvote').addEventListener(
            'click',
            function(ev) {
                upvote_onoff_elem.classList.remove('on')
                downvote_onoff_elem.classList.add('on')

                incrementElem(upvote_count_elem, 1);
                if (has_downvote) {
                    incrementElem(downvote_count_elem, -1);
                    incrementElem(net_votes_elem, 2);
                } else {
                    incrementElem(net_votes_elem, 1);
                }

                has_downvote = false;
                has_upvote = true;
            },
            false
        )
        document.getElementById('undo-upvote').addEventListener(
            'click',
            function(ev) {
                upvote_onoff_elem.classList.add('on')
                incrementElem(upvote_count_elem, -1);
                incrementElem(net_votes_elem, -1);
                has_upvote = false;
            },
            false
        )
        document.getElementById('downvote').addEventListener(
            'click',
            function(ev) {
                downvote_onoff_elem.classList.remove('on')
                upvote_onoff_elem.classList.add('on')

                incrementElem(downvote_count_elem, 1);
                if (has_upvote) {
                    incrementElem(upvote_count_elem, -1);
                    incrementElem(net_votes_elem, -2);
                } else {
                    incrementElem(net_votes_elem, -1);
                }

                has_downvote = true;
                has_upvote = false;
            },
            false
        )
        document.getElementById('undo-downvote').addEventListener(
            'click',
            function(ev) {
                downvote_onoff_elem.classList.add('on')
                incrementElem(downvote_count_elem, -1);
                incrementElem(net_votes_elem, 1);
                has_downvote = false;
            },
            false
        )
    }
};
