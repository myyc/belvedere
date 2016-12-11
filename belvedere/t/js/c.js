var d = new $jqOpta.Deferred;

d.resolveWith = function (a, b) {
    a.done(b[0].d);
};

d.done = function (a) {
    var t = [];
    a = a.split("¦");
    var d = ["id", "full", "short", "abbr"];

    for (var b = 0; b < a.length; b++) {
        var c = a[b].split("|");
        if (c[0] && c[0].length > 0) {
            var o = {id: parseInt(c[0])};
            for(var i = 1; i < 4; i++) {
                if(c[i] && c[i].length > 0) {
                    o[d[i]] = c[i];
                }
            }
            if("full" in o) {
                t.push(o);
            }
        }
    }
    var s = JSON.stringify(t);
    document.getElementById("main").innerHTML = btoa(String.fromCharCode.apply(null, pako.deflate(s)));
    document.getElementById("conf").innerHTML = "yes";
};

var p = {
    competition: {{ cid }},
    cust_id: "default",
    trans_id: 1,
    lang_id: "en_GB",
    sport_id: "1",
    season: {{ season }}
};

var r = new $jqOpta.FeedRequest(
    $jqOpta.FeedRequest.{{ feed }},
    p,
    d,
    99999);
$jqOpta.FeedMonitor.requestFeed(r);
