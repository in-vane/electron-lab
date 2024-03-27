export const CONST = {
  MIME: {
    img: ['png', 'png'],
    pdf: ['pdf', 'pdf'],
    excel: ['vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'xlsx'],
  },
  MODE_PDF2IMG: {
    MODE_NORMAL: 0,
    MODE_VECTOR: 1,
  },
};

export const handleDownload = (value, fileType) => {
  const mime = CONST.MIME[fileType];
  // 将 base64 编码的字符串转换成二进制数据
  const byteCharacters = atob(value);
  const byteNumbers = new Array(byteCharacters.length);

  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);

  // 创建一个 Blob 对象
  const blob = new Blob([byteArray], { type: `application/${mime[0]}` });

  // 生成一个临时的 URL
  const url = URL.createObjectURL(blob);
  // 创建一个链接并设置下载属性
  const a = document.createElement('a');
  a.href = url;
  a.download = `result.${mime[1]}`;
  a.click();

  // 释放临时的 URL
  URL.revokeObjectURL(url);
};

export const scrollInneHeight = () => {
  window.scrollTo({
    top: window.innerHeight,
    behavior: 'smooth',
  });
};
