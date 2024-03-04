
import os
import OpenSSL.crypto
from OpenSSL import crypto
import json
import pickle
import sys

from array import *
from jinja2 import Environment
from jinja2 import FileSystemLoader
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import NotFound
from werkzeug.routing import Map
from werkzeug.routing import Rule
from werkzeug.urls import url_parse
from werkzeug.utils import redirect
from werkzeug.wrappers import Request
from werkzeug.wrappers import Response

from SSearch import SSearch, SSearchVersion, SSearchLogger

logger = SSearchLogger().getLogger()


def get_hostname(url):
    return url_parse(url).netloc

class SSearchServer(object):
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SSearchServer, cls).__new__(cls)

        # Put any initialization here.
        
        return cls._instance
        
    def __init__(self):
        logger.info("Starting Semantic Search Server...")
        template_path = os.path.join(os.path.dirname(__file__), "templates")
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_path), autoescape=True
        )
        self.jinja_env.filters["hostname"] = get_hostname
        # self.config  = config["config"]
        self.url_map = Map(
            [
                Rule("/", endpoint="new_url"),
                Rule("/<short_id>", endpoint="follow_short_link"),
                Rule("/<short_id>+", endpoint="short_link_details"),
                Rule("/version", endpoint="version"),
                Rule("/ssearch", endpoint="ssearch")
            ]
        )
        self.ssearch = SSearch()
        # Load sentences & embeddings from disc
        with open("embeddings.pkl", "rb") as fIn:
            stored_data = pickle.load(fIn)
            stored_sentences = stored_data["sentences"]
            stored_embeddings = stored_data["embeddings"]
    

    def on_version(self, request):
        return Response( json.dumps(SSearchVersion().__dict__, default=lambda o: o.__dict__) )

    '''
    Semantic Search
    '''
    def on_ssearch(self, request):
        error = None
        url = ""
        print("Inside semantic search")
        print(request.method)
        if request.method == "POST" or request.method == "GET":
            # json_data = json.loads(request.data.decode('UTF-8'))
            print("Inside GET/POST: " + str(request.content_length))
            json_data = request.get_json()
            print("Real json: "  + json_data)
            print("Real data:" + request.get_data())
            print("Incoming data: " + json.dumps(json_data ) )
            query = json_data["query"]
            return Response(self.ssearch.doSearch(query))

        self.ssearch.status = "HTTP_METHOD_ERROR"
        return Response( json.dumps(self.ssearch.__dict__, default=lambda o: o.__dict__) )


    def on_new_url(self, request):
        error = None
        url = ""
        if request.method == "POST":
            return Response("Main Page")
            url = request.form["url"]
            if not is_valid_url(url):
                error = "Please enter a valid URL"
            else:
                short_id = self.insert_url(url)
                return redirect(f"/{short_id}+")
        return self.render_template("index.html", error=error, url=url)

    def on_follow_short_link(self, request, short_id):
        # link_target = self.redis.get(f"url-target:{short_id}")
        link_target = short_id
        if link_target is None:
            raise NotFound()
        # self.redis.incr(f"click-count:{short_id}")
        return redirect(link_target)

    def on_short_link_details(self, request, short_id):
        # link_target = self.redis.get(f"url-target:{short_id}")
        link_target = short_id
        if link_target is None:
            raise NotFound()
        # click_count = int(self.redis.get(f"click-count:{short_id}") or 0)
        return self.render_template(
            "short_link_details.html",
            link_target=link_target,
            short_id=short_id,
            click_count=click_count,
        )

    def error_404(self):
        response = self.render_template("404.html")
        response.status_code = 404
        return response

    def insert_url(self, url):
        # short_id = self.redis.get(f"reverse-url:{url}")
        short_id = url
        if short_id is not None:
            return short_id
        url_num = self.redis.incr("last-url-id")
        short_id = base36_encode(url_num)
        self.redis.set(f"url-target:{short_id}", url)
        self.redis.set(f"reverse-url:{url}", short_id)
        return short_id

    def render_template(self, template_name, **context):
        t = self.jinja_env.get_template(template_name)
        return Response(t.render(context), mimetype="text/html")

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        logger.debug(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, f"on_{endpoint}")(request, **values)
        except NotFound:
            return self.error_404()
        except HTTPException as e:
            return e

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        # print(request)
        # print(start_response)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
