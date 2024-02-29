import { app, BrowserWindow } from 'electron';
import path from 'path';
import { spawn } from 'child_process';

const __dirname = path.resolve();

app.whenReady().then(() => {
  const win = new BrowserWindow({
    title: 'Main window',
    webPreferences: {
      webSecurity: false, // 避免跨域问题
      contextIsolation: true,
      devTools: true,
    },
  });

  // You can use `process.env.VITE_DEV_SERVER_URL` when the vite command is called `serve`
  if (process.env.VITE_DEV_SERVER_URL) {
    win.loadURL(process.env.VITE_DEV_SERVER_URL);
  } else {
    // Load your file
    win.loadFile('dist/index.html');
  }
});

let pyProcess = null;

function createPyProcess() {
  if (pyProcess != null) {
    console.log('child proces already exists');
  } else {
    let port = '4242';
    let script;
    if (process.env.VITE_DEV_SERVER_URL) {
      // 开发模式下直接使用python脚本
      script = path.join(__dirname, 'python', 'api.py');
      pyProcess = spawn('python', ['-u', script, '--port=' + port]); // '-u' 的目的是将python的输出设置为无缓冲，使得python的输出及时发送到electron
    } else {
      // 部署模式下使用打包后的python程序
      script = path.join('dist-python', 'api.exe');
      pyProcess = spawn(script, ['--port=' + port]);
    }
    if (pyProcess != null) {
      console.log('start child process success');
      if (pyProcess.stdout != null) {
        // 显示python标准输出流
        pyProcess.stdout.on('data', (data) => {
          console.log(`child process stdout: ${data}`);
        });
      }
      if (pyProcess.stderr != null) {
        // 显示python异常输出流
        pyProcess.stderr.on('data', (data) => {
          console.log(`child process stderr: ${data}`);
        });
      }
    } else {
      console.log('faild to start chile process');
    }
  }
}

function exitPyProcess() {
  if (pyProcess != null) {
    pyProcess.kill();
    pyProcess = null;
    console.log('success kill child process');
  } else {
    console.log('child process does not exist');
  }
}

app.on('ready', createPyProcess);
app.on('will-quit', exitPyProcess);
