import json
import asyncio
import tornado
import tornado.web
import tornado.websocket
import tornado.options
import tornado.ioloop
import tasks


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
            (r'/ce', MainHandler),
            (r'/explored', MainHandler),
            (r'/size', MainHandler),
            (r'/pageNumber', MainHandler),
            (r'/table', MainHandler),
            (r'/screw', MainHandler),
            (r'/language', MainHandler),
            (r"/api", ApiHandler),
        ]
        settings = {
        }
        super().__init__(handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, PUT, DELETE, OPTIONS')
        self.set_header('Access-Control-Allow-Headers', 'Content-Type')
        self.set_header('Access-Control-Expose-Headers', 'Content-Type')
    
    def options(self):
        self.set_status(200)
        self.finish()
        
    def post(self):
        print("===== post =====")

        file_list_keys = self.request.files.keys()
        file_list = []
        custom_data = {}

        for _, key in enumerate(file_list_keys):
            _file = self.request.files[key][0]
            file_list.append(_file['body'])

        if self.request.path == '/ce':
            image_base64 = tasks.compare_ce(file_list[0],file_list[1])
            custom_data = {"data": f"data:image/jpeg;base64,{image_base64}"}
        elif self.request.path == '/explored':
            image_base64 = tasks.compare_explored(file_list[0],file_list[1])
            custom_data = {"data": f"data:image/jpeg;base64,{image_base64}"}
        elif self.request.path == '/size':
            image_base64 = tasks.compare_size(file_list[0])
            custom_data = {"data": f"data:image/jpeg;base64,{image_base64}"}
        elif self.request.path == '/pageNumber':
            doc_base64, error_page = tasks.check_page(file_list[0])
            custom_data = {"data": doc_base64, "error_page": error_page}
        elif self.request.path == '/table':
            doc_base64, error_page = tasks.compare_table(file_list[0])
            custom_data = {"data": doc_base64, "error_page": error_page}
        elif self.request.path == '/screw':
            doc_base64 = tasks.check_screw(file_list[0])
            custom_data = {"data": doc_base64}
        elif self.request.path == '/language':
            is_error, error_language = tasks.check_language(file_list[0])
            custom_data = {"is_error": is_error, "error_language": error_language}
        elif self.request.path == '/other':
            pass
 
        self.write(custom_data)


class ApiHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("websocket opened")

        self.temp_count = 0
        self.loop = tornado.ioloop.PeriodicCallback(self.check_per_seconds, 1000)
        self.loop.start()  # 启动一个循环，每秒向electron端发送数字，该数字在不断递增

    def on_message(self, message):
        print("get message: ", message)
        custom_data = {
            "data": "hello " + message
        }
        self.write_message(custom_data)

    def on_close(self):
        print("websocket closed")
        self.loop.stop()

    def check_per_seconds(self):
        self.write_message(tornado.escape.json_encode({"data": self.temp_count}))
        self.temp_count += 1
        

async def main():
    tornado.options.define("port", default=8888, help="run on the given port", type=int)
    tornado.options.parse_command_line()
    app = Application()
    app.listen(tornado.options.options.port)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())