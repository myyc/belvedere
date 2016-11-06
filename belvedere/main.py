import os
import time

import cherrypy
from jinja2 import Environment, FileSystemLoader
from selenium import webdriver
import redis

env = Environment(loader=FileSystemLoader("t"))
cd = os.path.dirname(os.path.abspath(__file__))
port = 9080


class Root:
    @staticmethod
    def get_main():
        return env.get_template("main.html")

    @cherrypy.expose
    def jc(self, cid, season=2016):
        t = env.get_template("js/c.js")
        if cid == "0":
            cid = "null"
            feed = "FEED_TRANS_COMP"
        else:
            feed = "FEED_TRANS_TEAM"
        return t.render(season=season, cid=cid, feed=feed)

    @cherrypy.expose
    def jf(self, feed, season=2016, cid=None, team=None, gid=None):
        t = env.get_template("js/f.js")
        return t.render(season=season, cid=cid, feed=feed, team=team,
                        gid=gid)

    @staticmethod
    def froute(feed, cid, team=None, gid=None, season=2016, html=True):
        return ("/{p}/{feed}/{season}/{cid}/"
                "{team}/{gid}").format(p="hf" if html else "jf", feed=feed,
                                       cid=cid, team=team, gid=gid,
                                       season=season)

    @staticmethod
    def scrape(url):
        cherrypy.response.headers["Content-Type"] = "text/json"
        r = redis.Redis()
        if url in r:
            return r[url].decode("utf-8")

        driver = webdriver.PhantomJS()

        driver.get("http://127.0.0.1:{}/".format(port) + url)

        s = 0.
        while s <= 2:
            t = driver.find_element_by_id("main").text
            if len(t) > 0:
                driver.quit()
                r[url] = t
                r.expire(url, 3600)
                return t
            s += 0.1
            time.sleep(0.1)

        driver.quit()
        return "{}"

    @cherrypy.expose
    def hc(self, cid=0, season=2016):
        t = self.get_main()
        return t.render(route="/jc/{}/{}".format(cid, season))

    @cherrypy.expose
    def hf(self, feed, season=2016, cid=None, team=None, gid=None):
        t = self.get_main()

        if cid is None:
            raise ValueError("cid: None")
        if feed == "FEED_F1" or feed == "FEED_F24":
            team = "null"
        if feed != "FEED_F24":
            gid = "null"

        return t.render(route=self.froute(feed=feed, cid=cid, team=team,
                                          gid=gid, season=season, html=False))

    @cherrypy.expose
    def comps(self, season=2016):
        url = "/hc/0/{}/".format(season)

        return self.scrape(url)

    @cherrypy.expose
    def clubs(self, cid, season=2016):
        url = "/hc/{}/{}".format(cid, season)

        return self.scrape(url)

    @cherrypy.expose
    def games(self, cid, season=2016):
        feed = "FEED_F1"
        url = self.froute(feed=feed, cid=cid, season=season)

        return self.scrape(url)

    @cherrypy.expose
    def stats(self, cid, team, season=2016):
        feed = "FEED_F30"

        url = self.froute(feed=feed, cid=cid, season=season, team=team)

        return self.scrape(url)

    @cherrypy.expose
    def game(self, cid, gid, season=2016):
        feed = "FEED_F24"
        url = self.froute(feed=feed, cid=cid, gid=gid, season=season)

        return self.scrape(url)


cherrypy.config.update({"server.socket_host": "127.0.0.1",
                        "server.socket_port": port,
                        "tools.staticdir.on": True,
                        "tools.staticdir.dir": cd + "/s",
                        })

cherrypy.quickstart(Root())
