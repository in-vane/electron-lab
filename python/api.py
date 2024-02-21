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
        print(self.request.path)
        file_list_keys = self.request.files.keys()
        file_list = []
        for _, key in enumerate(file_list_keys):
            print(key)
            _file = self.request.files[key][0]
            file_list.append(_file['body'])
        if self.request.path == '/ce':
            image_base64 = tasks.compare_ce(file_list[0],file_list[1])
        elif self.request.path == '/explored':
            image_base64 = tasks.compare_explored(file_list[0],file_list[1])
        elif self.request.path == '/size':
            image_base64 = tasks.compare_size(file_list[0])
        elif self.request.path == '/other':
            pass
        custom_data = {"data": f"data:image/jpeg;base64,{image_base64}"}
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