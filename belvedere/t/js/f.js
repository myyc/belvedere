var p = {
    life: 60,
    params: {
        competition: {{ cid }},
        season: {{ season }},
        sport: "football",
        team: {{ team }},
        match: {{ gid }},
        player: {{ player }}
    }
};

var d = new $jqOpta.Deferred;
d.done(function (a) {
    var s = pako.deflate(JSON.stringify(a));
    var r = [],
        l = s.length,
        cs = 65535;

    // lol
    if (s.slice === undefined) {
        s.slice = Array.prototype.slice;
    }

    for (var i = 0; i < l / cs; i++) {
        r.push(btoa(String.fromCharCode.apply(null, s.slice(i*cs, (i+1)*cs))))
    }

    document.getElementById("main").innerHTML = r.join("");
    document.getElementById("conf").innerHTML = "yes";
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
