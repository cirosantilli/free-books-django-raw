// http://stackoverflow.com/a/1714899/895245
var urlencode = function(obj) {
    var str = []
    for (var p in obj) {
        if (obj.hasOwnProperty(p)) {
            str.push(encodeURIComponent(p) + '=' + encodeURIComponent(obj[p]))
        }
    }
    return str.join('&')
}

/* Increment the integer text value that is the only child of a given element. */
var incrementElem = function(elem, delta) {
    elem.innerHTML = parseInt(elem.innerHTML) + delta
}

// http://stackoverflow.com/a/35385518/895245
function htmlToElements(html) {
    var template = document.createElement('template')
    template.innerHTML = html
    return template.content.childNodes
}

function insertBefore(newElem, oldElem) {
    oldElem.parentElement.insertBefore(newElem, oldElem)
}

/*
When the link elem is clicked, send an XHR to it's href,
with POST data taken from the data-* fields.
*/
var addSendXhrDataClickCallback = function(elem, successCallback, extraParamsCallback) {
    if (typeof successCallback  === 'undefined') {
        successCallback = function(xhr, currentTarget) {}
    }
    if (typeof extraParamsCallback  === 'undefined') {
        extraParamsCallback = function(currentTarget) { return {}; }
    }
    elem.addEventListener(
        'click',
        function(event) {
            event.preventDefault()
            var x = new XMLHttpRequest()
            // TODO required, why? Otherwise event.currentTarget is null inside the XHR.
            var currentTarget = event.currentTarget
            x.open('POST', currentTarget.getAttribute('href'), true)
            x.setRequestHeader('X-CSRFToken', Cookies.get('csrftoken'))
            x.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded;charset=utf-8')
            x.onreadystatechange = function() {
                if (x.readyState == 4) {
                    if (x.status != 200) {
                        alert('Action failed. Reload the page and try again.')
                    } else {
                        successCallback(x, currentTarget)
                    }
                }
            }
            params = currentTarget.dataset
            extraParams = extraParamsCallback(currentTarget)
            for (var attrname in extraParams) {
                params[attrname] = extraParams[attrname]
            }
            x.send(urlencode(params))
        },
        false
    )
}

window.onload = function() {
    var view = document.body.getAttribute('data-view')
    var data_js_json = JSON.parse(document.body.dataset['jsJson'])
    if (view === 'article_detail') {
        // Article votes
        {

            var addVoteHandlers = function(root) {
                // Send request to server.
                var elements = root.querySelectorAll('.vote')
                for (var i = 0; i < elements.length; i++) {
                    addSendXhrDataClickCallback(elements[i])
                }
            }

            addVoteHandlers(document)

            // Optimistically update the UI locally.
            var upvote_count_elem = document.getElementById('upvote-count')
            var upvote_onoff_elem = document.getElementById('upvote-onoff')
            var downvote_count_elem = document.getElementById('downvote-count')
            var downvote_onoff_elem = document.getElementById('downvote-onoff')
            var net_votes_elem = document.getElementById('net-votes')
            var has_upvote = document.querySelectorAll('#upvote-onoff.on #upvote').length === 0
            var has_downvote = document.querySelectorAll('#downvote-onoff.on #downvote').length === 0
            document.getElementById('upvote').addEventListener(
                'click',
                function(ev) {
                    upvote_onoff_elem.classList.remove('on')
                    downvote_onoff_elem.classList.add('on')

                    incrementElem(upvote_count_elem, 1)
                    if (has_downvote) {
                        incrementElem(downvote_count_elem, -1)
                        incrementElem(net_votes_elem, 2)
                    } else {
                        incrementElem(net_votes_elem, 1)
                    }

                    has_downvote = false
                    has_upvote = true
                },
                false
            )
            document.getElementById('undo-upvote').addEventListener(
                'click',
                function(ev) {
                    upvote_onoff_elem.classList.add('on')
                    incrementElem(upvote_count_elem, -1)
                    incrementElem(net_votes_elem, -1)
                    has_upvote = false
                },
                false
            )
            document.getElementById('downvote').addEventListener(
                'click',
                function(ev) {
                    downvote_onoff_elem.classList.remove('on')
                    upvote_onoff_elem.classList.add('on')

                    incrementElem(downvote_count_elem, 1)
                    if (has_upvote) {
                        incrementElem(upvote_count_elem, -1)
                        incrementElem(net_votes_elem, -2)
                    } else {
                        incrementElem(net_votes_elem, -1)
                    }

                    has_downvote = true
                    has_upvote = false
                },
                false
            )
            document.getElementById('undo-downvote').addEventListener(
                'click',
                function(ev) {
                    downvote_onoff_elem.classList.add('on')
                    incrementElem(downvote_count_elem, -1)
                    incrementElem(net_votes_elem, 1)
                    has_downvote = false
                },
                false
            )
        }

        // Tag votes.
        {
            var addArticleTagVoteHandlers = function(root) {
                var elements = root.querySelectorAll('.article-tag-vote')
                for (var i = 0; i < elements.length; i++) {
                    addSendXhrDataClickCallback(
                        elements[i],
                        undefined,
                        function(currentTarget) {
                            classList = currentTarget.classList
                            if (classList.contains('upvote')) {
                                isUpvote = true;
                                otherVoteElemClass = 'downvote'
                            } else {
                                isUpvote = false;
                                otherVoteElemClass = 'upvote'
                            }
                            parentElement = currentTarget.parentElement
                            otherVoteElem = parentElement.getElementsByClassName(otherVoteElemClass)[0]
                            otherVoteElemClassList = otherVoteElem.classList
                            tagVoteScoreElem = parentElement.getElementsByClassName('count')[0]
                            tagVoteCountElem = currentTarget.closest('.article-tag-vote-all').getElementsByClassName('article-tag-vote-count')[0]
                            if (classList.contains('on')) {
                                classList.remove('on')
                                if (otherVoteElemClassList.contains('on')) {
                                    tagVoteScoreDelta = 1
                                    tagVoteCountDelta = 1
                                } else {
                                    tagVoteScoreDelta = 2
                                    tagVoteCountDelta = 0
                                }
                                if (!isUpvote) {
                                    tagVoteScoreDelta *= -1
                                }
                                otherVoteElem.classList.add('on')
                            } else {
                                classList.add('on')
                                if (isUpvote) {
                                    tagVoteScoreDelta = -1
                                } else {
                                    tagVoteScoreDelta = 1
                                }
                                tagVoteCountDelta = -1
                            }
                            incrementElem(tagVoteScoreElem, tagVoteScoreDelta)
                            incrementElem(tagVoteCountElem, tagVoteCountDelta)
                        }
                    )
                }
            }

            addArticleTagVoteHandlers(document)

            var send_tag_xhr = function(event, ui) {
                if (!ui.duringInitialization) {
                    var x = new XMLHttpRequest()
                    var target = event.target
                    x.open('POST', target.getAttribute('data-url'), true)
                    x.setRequestHeader('X-CSRFToken', Cookies.get('csrftoken'))
                    x.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded;charset=utf-8')
                    x.onreadystatechange = function() {
                        if (x.readyState == 4) {
                            if (x.status != 200) {
                                alert('Action failed. Reload the page and try again.')
                            }
                        }
                    }
                    var dataset = target.dataset
                    var data = ['article', 'defined_by_article', 'type', 'value'].reduce(
                        function(o, k) { v = dataset[k]; if (v) { o[k] = v}; return o; }, {})
                    data.name = ui.tagLabel
                    x.send(urlencode(data))
                }
            }

            // tag-it for my tags.
            $('.my-tags').tagit({
                beforeTagAdded: function(event, ui) {
                    send_tag_xhr(event, ui)
                },
                beforeTagRemoved: function(event, ui) {
                    send_tag_xhr(event, ui)
                },
                onTagExists: function(event, ui) {
                    // TODO shows twice?
                    alert('Tag already exsists.')
                    return false
                },
            })

            // Load more votes.
            var elements = document.querySelectorAll('.get-more-votes')
            var loadMoreVotesLimit = data_js_json['loadMoreVotesLimit']
            var loadMoreVotesDefinedNextOffset = {
                '0': loadMoreVotesLimit,
                '1': loadMoreVotesLimit
            }
            for (var i = 0; i < elements.length; i++) {
                addSendXhrDataClickCallback(
                    elements[i],
                    function(xhr, currentTarget) {
                        jsonResponse = JSON.parse(xhr.responseText)
                        var span = document.createElement('span')
                        span.innerHTML = jsonResponse.html
                        addArticleTagVoteHandlers(span)
                        insertBefore(span, currentTarget)
                        loadMoreVotesDefinedNextOffset[currentTarget.dataset.defined] += loadMoreVotesLimit
                        if (!jsonResponse.with_score_has_more) {
                            currentTarget.parentElement.removeChild(currentTarget)
                        }
                    },
                    function(currentTarget) {
                        return {'offset': loadMoreVotesDefinedNextOffset[currentTarget.dataset.defined]}
                    }
                )
            }

            // select2 attempt.
            {
                /*
                $('.js-my-tags').select2({
                    tags: true,
                    tokenSeparators: [',', ' '],
                    width: '500px'
                }).on('change', function(e) {
                    if (e.removed) {
                        alert('remove')
                        $.ajax({
                            type: "POST",
                            url: '/admin/?controller=vouchers&action=updateRelatedProducts',
                            data: {id: e.removed.id, action: remove},    //Or you can e.removed.text
                            error: function () {
                                alert("error")
                            }
                        })
                    }
                    if (e.added) {
                        alert('add')
                        $.ajax({
                            type: "POST",
                            url: '/admin/?controller=vouchers&action=updateRelatedProducts',
                            data: {id: e.added.id, action: add},    //Or you can e.added.text
                            error: function () {
                                alert("error")
                            }
                        })
                    }
                })
                */
                /*
                .on("select2:select", function(e) {
                    if(e.params.data.isNew){
                        alert(e)
                        // append the new option element prenamently:
                        $(this).find('[value="'+e.params.data.id+'"]').replaceWith('<option selected value="'+e.params.data.id+'">'+e.params.data.text+'</option>')
                        // store the new tag:
                        $.ajax({
                            // ...
                        })
                    }
                })
                */
            }
        }
    }
}
