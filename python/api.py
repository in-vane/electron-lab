import json
import asyncio
import tornado
import tornado.web
import tornado.websocket
import tornado.options
import tornado.ioloop

import tasks
from utils import PdfAssembler

BASE64_IMG = 'data:image/jpeg;base64,'

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
            (r'/ce', MainHandler),
            (r'/explore/pdf2img', MainHandler),
            (r'/explore/compare', MainHandler),
            (r'/contours', MainHandler),
            (r'/size', MainHandler),
            (r'/pageNumber', MainHandler),
            (r'/table', MainHandler),
            (r'/screw', MainHandler),
            (r'/language', MainHandler),
            (r'/camera', MainHandler),
            (r"/api", ApiHandler),
        ]
        settings = {
            'debug': True
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
        arguments_keys = self.request.arguments.keys()
        file_list = []
        arguments = []
        custom_data = {}

        # 处理接收到的文件
        for _, key in enumerate(file_list_keys):
            _file = self.request.files[key][0]
            file_list.append(_file['body'])

        # 处理接收到的参数对象（这里只处理base64）
        for _, key in enumerate(arguments_keys):
            _argument = self.request.arguments[key][0]
            comma_index = _argument.find(b',')
            base64_data = _argument[comma_index + 1:]
            arguments.append(base64_data)

        # 路由分发
        if self.request.path == '/ce':
            xls_base64 = tasks.check_CE_mode_normal(file_list[0], file_list[1])
            custom_data = {"data": xls_base64}
            pass

        elif self.request.path == '/explore/pdf2img_single':
            imgs_path = tasks.pdf2img_single(file_list[0])
            custom_data = {"data": imgs_path}
            pass

        elif self.request.path == '/explore/pdf2img':
            data = []
            for file in file_list: 
                img_base64, image_base64_s = tasks.pdf2img(file)
                data.append([f"{BASE64_IMG}{img_base64}", f"{BASE64_IMG}{image_base64_s}"])
            custom_data = {"data": data}
            pass

        elif self.request.path == '/explore/compare':
            img_base64 = tasks.compare_explore(arguments[0], arguments[1])
            custom_data = {"data": f"{BASE64_IMG}{img_base64}"}
            pass

        elif self.request.path == '/contours':
            match_results = tasks.check_explore_part(img_base64=arguments[0], pdf=file_list[0], page_number=arguments[1])
            custom_data = {"match_results": match_results}
            pass

        elif self.request.path == '/size':
            is_error, msg, img_base64 = tasks.compare_size(file_list[0])
            custom_data = {"data": f"{BASE64_IMG}{img_base64}", "is_error": is_error, "msg": msg}
            pass

        elif self.request.path == '/pageNumber':
            error_pages_base64, error_page = tasks.check_page_number(file_list[0])
            custom_data = {"data": error_pages_base64, "error_page": error_page}
            pass

        elif self.request.path == '/table':
            doc_base64, error_page = tasks.compare_table(file_list[0])
            custom_data = {"data": doc_base64, "error_page": error_page}
            pass

        elif self.request.path == '/screw':
            doc_base64 = tasks.check_screw(file_list[0])
            custom_data = {"data": doc_base64}
            pass

        elif self.request.path == '/language':
            is_error, language_page, matched, mismatched = tasks.check_language(file_list[0])
            custom_data = {
                "is_error": is_error,
                "language_page": language_page,
                "matched": matched,
                "mismatched": mismatched
            }
            pass

        elif self.request.path == '/camera':
            img_base64_pic, img_base64_doc = tasks.check_camera(img_base64=arguments[0], pdf=file_list[0])
            custom_data = {"img_base64_pic": f"{BASE64_IMG}{img_base64_pic}", "img_base64_doc": f"{BASE64_IMG}{img_base64_doc}"}
            pass

        elif self.request.path == '/other':
            pass
 
        self.write(custom_data)


class ApiHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assemblers = {}

    def check_origin(self, origin):
        return True

    def open(self):
        print("websocket opened")

        self.temp_count = 0
        self.loop = tornado.ioloop.PeriodicCallback(self.check_per_seconds, 1000)
        self.loop.start()  # 启动一个循环，每秒向electron端发送数字，该数字在不断递增

    async def on_message(self, message):
        print("===== get_message =====")

        data = tornado.escape.json_decode(message)
        file_name = data.get('fileName')
        current_slice = data.get('currentSlice')
        total_slice = data.get('totalSlice')
        file_data = data.get('file')

        if file_name not in self.assemblers:
            self.assemblers[file_name] = PdfAssembler(file_name, total_slice)
        
        assembler = self.assemblers[file_name]
        assembler.add_slice(current_slice, file_data)
        
        if assembler.is_complete():
            assembled_pdf_path = assembler.assemble_pdf()
            if assembled_pdf_path:
                print(f"PDF assembled: {assembled_pdf_path}")
                # 可以在这里执行任何其他操作，例如将文件发送给客户端
                await tasks.pdf2img_single(self, assembled_pdf_path)
                # 然后清理已完成的 assembler
                del self.assemblers[file_name]

        custom_data = {"data": "return message"}
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