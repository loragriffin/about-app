import os

import boto3

import tornado.ioloop
import tornado.web
import tornado.log

from dotenv import load_dotenv

from jinja2 import \
    Environment, PackageLoader, select_autoescape

load_dotenv('.env')

PORT = int(os.environ.get('PORT', '8888'))

ENV = Environment(
    loader=PackageLoader('myapp', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


SES_client = boto3.client(
    'ses',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
    region_name="us-east-1"
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
        self.render_template("home.html", {})


class SubmittedHandler(TemplateHandler):
    def post(self):
        first_name = self.get_body_argument('first_name')

        self.render_template("contact-submitted.html", {'first_name': first_name})


class PageHandler(TemplateHandler):
    def post(self, page):
        first_name = self.get_body_argument('first_name')
        last_name = self.get_body_argument('last_name')
        subject = self.get_body_argument('subject')
        message = self.get_body_argument('message')

        response = SES_client.send_email(
            Destination={
                'ToAddresses': ['lora.jean@me.com'],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': 'UTF-8',
                        'Data': 'Name: {} {}\nSubject: {}\nMessage: {}'.format(first_name, last_name, subject, message),
                    },
                },
                'Subject': {'Charset': 'UTF-8', 'Data': '{}'.format(subject)},
            },
            Source='lora.jean@me.com'
        )
        self.redirect("/page/contact-submitted.html")

    def get(self, page):
        self.set_header(
            'Cache-Control',
            'no-store, no-cache, must-revalidate, max-age=0')
        print(page)
        self.render_template(page, {})


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/submitted", SubmittedHandler),
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
