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

/*
When the link elem is clicked, send an XHR to it's href,
with POST data taken from the data-* fields.

If the element has an ID `id`, and if there as textarea with id `ID-input`,
then the value of that input element is also sent on the XHR.
*/
var addDataPostClickCallback = function(elem) {
    elem.addEventListener(
        'click',
        function(event) {
            event.preventDefault();
            var x = new XMLHttpRequest();
            // TODO required, why? Otherwise event.currentTarget is null inside the XHR.
            var currentTarget = event.currentTarget;
            x.open('POST', currentTarget.getAttribute('href'), true);
            x.setRequestHeader('X-CSRFToken', Cookies.get('csrftoken'));
            x.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded;charset=utf-8');
            x.onreadystatechange = function() {
                if (x.readyState == 4) {
                    if (x.status != 200) {
                        // TODO translate this.
                        alert('Action failed. Reload the page and try again.');
                    }
                }
            }
            x.send(urlencode(currentTarget.dataset));
        },
        false
    );
}

window.onload = function() {
    var view = document.body.getAttribute('data-view');
    if (view === 'article_detail') {
        // Article votes
        {
            // Send request to server.
            var elements = document.querySelectorAll('.vote');
            for (var i = 0; i < elements.length; i++) {
                addDataPostClickCallback(elements[i]);
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

        // Tag votes.
        {
            var send_tag_xhr = function(event, ui) {
                if (!ui.duringInitialization) {
                    var x = new XMLHttpRequest();
                    var target = event.target;
                    x.open('POST', target.getAttribute('data-url'), true);
                    x.setRequestHeader('X-CSRFToken', Cookies.get('csrftoken'));
                    x.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded;charset=utf-8');
                    x.onreadystatechange = function() {
                        if (x.readyState == 4) {
                            if (x.status != 200) {
                                alert('Action failed. Reload the page and try again.');
                            }
                        }
                    }
                    var dataset = target.dataset;
                    var data = ['article', 'defined-by-article', 'type', 'value'].reduce(
                        function(o, k) { o[k] = dataset[k]; return o; }, {})
                    data.name = ui.tagLabel;
                    x.send(urlencode(data));
                }
            }

            // tag-it
            $('.my-tags').tagit({
                beforeTagAdded: function(event, ui) {
                    send_tag_xhr(event, ui);
                },
                beforeTagRemoved: function(event, ui) {
                    send_tag_xhr(event, ui);
                },
                onTagExists: function(event, ui) {
                    // TODO shows twice?
                    alert('Tag already exsists.');
                    return false;
                },
            });

            // select2 attempt.
            {
                /*
                $('.js-my-tags').select2({
                    tags: true,
                    tokenSeparators: [',', ' '],
                    width: '500px'
                }).on('change', function(e) {
                    if (e.removed) {
                        alert('remove');
                        $.ajax({
                            type: "POST",
                            url: '/admin/?controller=vouchers&action=updateRelatedProducts',
                            data: {id: e.removed.id, action: remove},    //Or you can e.removed.text
                            error: function () {
                                alert("error");
                            }
                        });
                    }
                    if (e.added) {
                        alert('add');
                        $.ajax({
                            type: "POST",
                            url: '/admin/?controller=vouchers&action=updateRelatedProducts',
                            data: {id: e.added.id, action: add},    //Or you can e.added.text
                            error: function () {
                                alert("error");
                            }
                        });
                    }
                });
                */
                /*
                .on("select2:select", function(e) {
                    if(e.params.data.isNew){
                        alert(e);
                        // append the new option element prenamently:
                        $(this).find('[value="'+e.params.data.id+'"]').replaceWith('<option selected value="'+e.params.data.id+'">'+e.params.data.text+'</option>');
                        // store the new tag:
                        $.ajax({
                            // ...
                        });
                    }
                });
                */
            }
        }
    }
};
