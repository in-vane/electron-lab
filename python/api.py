import json
import asyncio
import tornado
import tornado.web
import tornado.websocket
import tornado.options
import tornado.ioloop

import tasks
from utils import PDFAssembler

CONTENT_TYPE_PDF = "application/pdf"
BASE64_PNG = 'data:image/png;base64,'
BASE64_JPG = 'data:image/jpeg;base64,'

class Application(tornado.web.Application):
    def __init__(self):
        test = 1
        handlers = [
            (r'/', MainHandler),
            (r'/ce', CEHandler),
            (r'/explore', ExploreHandler),
            (r'/partCount', PartCountHandler),
            (r'/size', SizeHandler),
            (r'/pageNumber', PageNumberHandler),
            (r'/table', TableHandler),
            (r'/screw', ScrewHandler),
            (r'/language', LanguageHandler),
            (r'/ocr_char', OcrHandler),
            (r'/ocr_icon', OcrHandler),
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
        
    def get_files(self):
        files = []
        for field_name, file in self.request.files.items():
            files.append(file[0])
        return files


class CEHandler(MainHandler):
    def post(self):
        mode = int(self.get_argument('mode'))
        files = self.get_files()
        file_1, file_2 = files[0], files[1]
        file_1_type, file_1_body = file_1["content_type"], file_1["body"]
        file_2_body = file_2["body"]
        if file_1_type == CONTENT_TYPE_PDF:
            file_pdf, file_excel = file_1_body, file_2_body
        else:
            file_pdf, file_excel = file_2_body, file_1_body
        img_base64 = ''
        if mode == 0:
            img_base64 = tasks.check_CE_mode_normal(file_excel, file_pdf)
        custom_data = {
            "result": f"{BASE64_PNG}{img_base64}"
        }
        self.write(custom_data)

class ExploreHandler(MainHandler):
    def post(self):
        img_1 = self.get_argument('img_1')
        img_2 = self.get_argument('img_2')
        img_base64 = tasks.compare_explore(img_1, img_2)
        custom_data = { "result": f"{BASE64_PNG}{img_base64}" }
        self.write(custom_data)

class PartCountHandler(MainHandler):
    def post(self):
        filename = self.get_argument('filename')
        rect = self.get_arguments('rect')
        rect_int = [int(x) for x in rect]
        page_number_explore = int(self.get_argument('pageNumberExplore'))
        page_number_table = int(self.get_argument('pageNumberTable'))
        error, result = tasks.check_part_count(filename, rect_int, page_number_explore, page_number_table)
        custom_data = {
            "error": error,
            "result": result
        }
        self.write(custom_data)

class PageNumberHandler(MainHandler):
    def post(self):
        files = self.get_files()
        file = files[0]
        body = file["body"]
        error, error_page, result = tasks.check_page_number(body)
        custom_data = {
            "error": error,
            "error_page": error_page,
            "result": result
        }
        self.write(custom_data)

class TableHandler(MainHandler):
    def post(self):
        page_number = int(self.get_argument('pageNumber'))
        files = self.get_files()
        file = files[0]
        body = file["body"]
        base64_imgs, error_pages = tasks.compare_table(body, page_number)
        custom_data = {
            "base64_imgs": base64_imgs,
            "error_pages": error_pages,
        }
        self.write(custom_data)

class ScrewHandler(MainHandler):
    def post(self):
        files = self.get_files()
        file = files[0]
        body = file["body"]
        result = tasks.check_screw(body)
        custom_data = {
            "error": True,
            "result": result
        }
        self.write(custom_data)

class LanguageHandler(MainHandler):
    def post(self):
        files = self.get_files()
        file = files[0]
        body = file["body"]
        error, content_page, result = tasks.check_language(body)
        custom_data = {
            "error": error,
            "content_page": content_page,
            "result": result
        }
        self.write(custom_data)

class SizeHandler(MainHandler):
    def post(self):
        files = self.get_files()
        file = files[0]
        filename, content_type, body = file["filename"], file["content_type"], file["body"]
        error, error_msg, img_base64 = tasks.compare_size(body) 
        custom_data = {
            "error": error,
            "error_msg": error_msg,
            "result": f"{BASE64_PNG}{img_base64}",
        }
        self.write(custom_data)

class OcrHandler(MainHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.MODE_CHAR = 0
        self.MODE_ICON = 1

    def post(self):
        mode = int(self.get_argument('mode'))
        custom_data = {}
        if mode == self.MODE_CHAR:
            print("== MODE_CHAR ==")
            img_base64 = self.get_argument('img_base64')
            files = self.get_files()
            file = files[0]
            body = file["body"]
            error, img_base64_pic, img_base64_doc = tasks.check_ocr_char(img_base64, body)
            custom_data = {
                "error": error,
                "result": [img_base64_pic, img_base64_doc],
            }
        if mode == self.MODE_ICON:
            print("== MODE_ICON ==")
            files = self.get_files()
            file_1, file_2 = files[0], files[1]
            body_1, body_2 = file_1["body"], file_2["body"]
            img1, img2 = tasks.check_ocr_icon(body_1, body_2)
            custom_data = {
                "result": [img1, img2],
            }
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
        type = data.get('type')

        if type == 'sendFileClip':
            index = data.get('index')
            file_name = data.get('fileName')
            current_slice = data.get('currentSlice')
            total_slice = data.get('totalSlice')
            file_data = data.get('file')

            if file_name not in self.assemblers:
                self.assemblers[file_name] = PDFAssembler(file_name, total_slice)
            
            assembler = self.assemblers[file_name]
            assembler.add_slice(current_slice, file_data)
            
            if assembler.is_complete():
                assembled_pdf_path = assembler.assemble_pdf()
                if assembled_pdf_path:
                    await tasks.pdf2img_single(self, assembled_pdf_path, index) # 可以在这里执行任何其他操作，例如将文件发送给客户端
                    del self.assemblers[file_name] # 然后清理已完成的 assembler

        custom_data = {"data": f"return {type}"}
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