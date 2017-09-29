import os

import tornado.ioloop
import tornado.web
import tornado.log

from jinja2 import \
    Environment, PackageLoader, select_autoescape

PORT = int(os.environ.get('PORT', '8888'))

ENV = Environment(
    loader=PackageLoader('myapp', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


class TemplateHandler(tornado.web.RequestHandler):
    def render_template(self, tpl, context):
        template = ENV.get_template(tpl)
        self.write(template.render(**context))


class MainHandler(TemplateHandler):
    def get(self):
        self.set_header(
            'Cache-Control',
            'no-store, no-cache, must-revalidate, max-age=0')
        self.render_template("\templates\base.html", {})


class PageHandler(TemplateHandler):
    def get(self, page):
        self.set_header(
            'Cache-Control',
            'no-store, no-cache, must-revalidate, max-age=0')
        print(page)
        self.render_template(page, {})


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/page/(.*)", PageHandler),
        (r"/static/(.*)",
         tornado.web.StaticFileHandler,
         {'path': 'static'}
         ),
    ], autoreload=True)


if __name__ == "__main__":
    tornado.log.enable_pretty_logging()

    app = make_app()
    app.listen(PORT, print('Server started on localhost: ' + str(PORT)))
    tornado.ioloop.IOLoop.current().start()
