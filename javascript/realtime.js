/*
 * Realtime updates over server sent events.
 *
 * Vote scores are patched in place, new posts and topics raise an
 * unobtrusive "new activity" bar that reloads the page when clicked.
 */
(function () {
    var tid = window.stream_tid;
    if (!tid || typeof window.EventSource === "undefined") {
        return;
    }

    var pending = 0,
        bar = null;

    function showBar(text) {
        if (!bar) {
            bar = document.createElement("div");
            bar.className = "realtime-bar";
            bar.onclick = function () { window.location.reload(); };
            document.body.appendChild(bar);
        }
        bar.innerHTML = text;
    }

    function updateScore(id, score) {
        var nodes = document.querySelectorAll('.score[data-id="' + id + '"]'),
            i;
        for (i = 0; i < nodes.length; i += 1) {
            nodes[i].innerHTML = score;
            nodes[i].className = "score score-updated";
        }
    }

    var src = new EventSource("/api/events/" + tid);

    src.onmessage = function (ev) {
        var data;
        try {
            data = JSON.parse(ev.data);
        } catch (err) {
            return;
        }

        if (data.event === "vote") {
            updateScore(data.tid, data.score);
            return;
        }

        pending += 1;
        showBar(pending === 1
                ? "1 new " + (data.event === "topic" ? "topic" : "post") + " &mdash; click to refresh"
                : pending + " new items &mdash; click to refresh");
    };
}());
