export const CONST = {};

export const handleDownload = (value, fileType) => {
  console.log(1);
  console.log(value);
  // 将 base64 编码的字符串转换成二进制数据
  const byteCharacters = atob(value);
  console.log(2);
  const byteNumbers = new Array(byteCharacters.length);
  console.log(3);
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);

  // 创建一个 Blob 对象
  const blob = new Blob([byteArray], { type: `application/${fileType}` });
  console.log(4);

  // 生成一个临时的 URL
  const url = URL.createObjectURL(blob);
  // 创建一个链接并设置下载属性
  const a = document.createElement('a');
  a.href = url;
  a.download = 'document.pdf';
  a.click();

  // 释放临时的 URL
  URL.revokeObjectURL(url);
};
