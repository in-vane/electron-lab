import base64
from io import BytesIO

import fitz

class PdfAssembler:
    def __init__(self, file_name, total_slices):
        self.file_name = file_name
        self.total_slices = total_slices
        self.received_slices = {}
        self.received_data = b''  # 用于存储所有分片数据
    
    def add_slice(self, current_slice, file_data):
        self.received_slices[current_slice] = file_data
    
    def is_complete(self):
        return len(self.received_slices) == self.total_slices
    
    def assemble_pdf(self):
        if not self.is_complete():
            return None
        
        # Sort received slices by current slice number
        sorted_slices = sorted(self.received_slices.items(), key=lambda x: x[0])
        
        for _, slice_data in sorted_slices:
            b64 = slice_data.split(",", 1)
            self.received_data += base64.b64decode(b64[1])
        
        output_path = self.file_name
        with open(output_path, "wb") as output_file:
            output_file.write(self.received_data)
        
        return output_path