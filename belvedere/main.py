import os
import json
import zlib
import base64

import cherrypy
from jinja2 import Environment, FileSystemLoader
import redis

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

env = Environment(loader=FileSystemLoader("t"))
cd = os.path.dirname(os.path.abspath(__file__))
port = 9080


class Root:
    @staticmethod
    def get_main():
        return env.get_template("main.html")

    @cherrypy.expose
    def jc(self, feed, cid="null", season=2016, team="null"):
        t = env.get_template("js/c.js")
        return t.render(season=season, cid=cid, feed=feed, team=team)

    @cherrypy.expose
    def jf(self, feed, season=2016, cid="null", team="null", gid="null",
           player="null"):
        t = env.get_template("js/f.js")
        return t.render(season=season, cid=cid, feed=feed, team=team,
                        gid=gid, player=player)

    @staticmethod
    def froute(feed, cid="null", team="null", gid="null", season=2016,
               player="null", html=True):
        return ("/{p}/{feed}/{season}/{cid}/"
                "{team}/{gid}/"
                "{player}").format(p="hf" if html else "jf",
                                   feed=feed, cid=cid, team=team, gid=gid,
                                   season=season, player=player)

    @cherrypy.expose
    def hc(self, feed, cid="null", season=2016, team="null"):
        t = self.get_main()
        return t.render(route="/jc/{}/{}/{}/{}".format(feed, cid, season,
                                                       team))

    @cherrypy.expose
    def hf(self, feed, season=2016, cid="null", team="null", gid="null",
           player="null"):
        t = self.get_main()

        if cid is None:
            raise ValueError("cid: None")

        return t.render(route=self.froute(feed=feed, cid=cid, team=team,
                                          gid=gid, season=season,
                                          player=player, html=False))

    @staticmethod
    def scrape(url):
        cherrypy.response.headers["Content-Type"] = "text/json"
        r = redis.Redis()
        if url in r:
            return r[url].decode("utf-8")

        driver = webdriver.PhantomJS()

        driver.get("http://127.0.0.1:{}/{}".format(port, url))

        try:
            wait = WebDriverWait(driver, 5)
            wait.until(ec.text_to_be_present_in_element((By.ID, "conf"),
                                                        "yes"))
            t = driver.find_element_by_id("main").text
        except TimeoutException:
            d = {"err": "timeout", "log": driver.get_log("browser")}
            d = zlib.compress(json.dumps(d).encode("utf-8"))
            return base64.b64encode(d)
        finally:
            driver.quit()

        r[url] = t
        r.expire(url, 3600)
        return t

    @cherrypy.expose
    def c(self, feed, cid="null", season=2016, team="null"):
        url = "/hc/{}/{}/{}/{}".format(feed, cid, season, team)

        return self.scrape(url)

    @cherrypy.expose
    def f(self, feed, season=2016, cid="null", team="null", gid="null",
          player="null"):
        url = self.froute(feed=feed, season=season, cid=cid, team=team,
                          gid=gid, player=player)

        return self.scrape(url)

    @cherrypy.expose
    def comps(self, season=2016):
        feed = "FEED_TRANS_COMP"
        url = "/hc/{}/null/{}/null".format(feed, season)

        return self.scrape(url)

    @cherrypy.expose
    def teams(self, cid, season=2016):
        feed = "FEED_TRANS_TEAM"
        url = "/hc/{}/{}/{}/null".format(feed, cid, season)

        return self.scrape(url)

    @cherrypy.expose
    def team(self, cid, team, season=2016):
        feed = "FEED_TRANS_PLAYER"
        url = "/hc/{}/{}/{}/{}".format(feed, cid, season, team)

        return self.scrape(url)

    def fscrape(self, **kwargs):
        url = self.froute(**kwargs)

        return self.scrape(url)

    @cherrypy.expose
    def table(self, cid, season=2016):
        return self.fscrape(**dict(feed="FEED_F3", cid=cid, season=season))

    @cherrypy.expose
    def games(self, cid, season=2016):
        return self.fscrape(**dict(feed="FEED_F1", cid=cid, season=season))

    @cherrypy.expose
    def stats(self, cid, team, season=2016):
        return self.fscrape(**dict(feed="FEED_F30", cid=cid, season=season,
                                   team=team))

    @cherrypy.expose
    def game(self, gid):
        return self.fscrape(**dict(feed="FEED_F24", gid=gid))

    @cherrypy.expose
    def lineup(self, gid):
        return self.fscrape(**dict(feed="FEED_F31", gid=gid))

    @cherrypy.expose
    def poss(self, gid):
        return self.fscrape(**dict(feed="FEED_F28", gid=gid))

    @cherrypy.expose
    def passes(self, gid, team):
        return self.fscrape(**dict(feed="FEED_F27a", team=team, gid=gid))

    @cherrypy.expose
    def refs(self, cid, season=2016):
        return self.fscrape(**dict(feed="FEED_F37", cid=cid, season=season))


cherrypy.config.update({"server.socket_host": "127.0.0.1",
                        "server.socket_port": port,
                        "tools.staticdir.on": True,
                        "tools.staticdir.dir": cd + "/s",
                        })

cherrypy.quickstart(Root())
