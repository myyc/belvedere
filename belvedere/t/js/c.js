var d = new $jqOpta.Deferred;

d.resolveWith = function (a, b) {
    a.done(b[0].d);
};

d.done = function (a) {
    var teams = [];
    a = a.split("¦");

    for (var b = 0; b < a.length; b++) {
        var c = a[b].split("|");
        if (c[1] && c[1].length > 0) {
            teams.push({id: c[0], full: c[1], short: c[2], abbr: c[3]});
        }
    }

    document.getElementById("main").innerHTML = JSON.stringify(teams);
};

var p = {
    competition: {{ cid }},
    cust_id: "default",
    trans_id: $jqOpta.settings.translation_id || 1,
    lang_id: "en_GB",
    sport_id: "1",
    season: {{ season }}
};

var teamRequest = new $jqOpta.FeedRequest(
    $jqOpta.FeedRequest.{{ feed }},
    p,
    d,
    99999);
$jqOpta.FeedMonitor.requestFeed(teamRequest);
