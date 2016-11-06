var p = {
    life: 60,
    params: {
        competition: {{ cid }},
        season: {{ season }},
        sport: "football",
        team: {{ team }},
        match: {{ gid }}
    }
};

var d = new $jqOpta.Deferred;
d.done(function (a) {
    document.getElementById("main").innerHTML = JSON.stringify(a);
});

var f = new $jqOpta.FeedRequest(
    $jqOpta.FeedRequest.{{ feed }},
    p.params,
    d,
    p.life,
    p.trn,
    p
);

$jqOpta.FeedMonitor.requestFeed(f);
