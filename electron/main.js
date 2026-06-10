const { app, BrowserWindow, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const net = require('net');

let mainWindow;
let backendProcess;

function startBackend() {
  const isDev = !app.isPackaged;
  const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
  const scriptPath = isDev
    ? path.join(__dirname, '..', 'backend', 'backend.py')
    : path.join(process.resourcesPath, 'backend', 'backend.py');

  backendProcess = spawn(pythonCmd, [scriptPath], {
    stdio: ['pipe', 'pipe', 'pipe']
  });

  backendProcess.stdout.on('data', (data) => {
    console.log(`[Backend] ${data}`);
  });
  backendProcess.stderr.on('data', (data) => {
    console.error(`[Backend Error] ${data}`);
  });
  backendProcess.on('error', (err) => {
    console.error('Failed to start backend:', err);
    dialog.showErrorBox('Ошибка', 'Не удалось запустить сервер. Проверьте наличие Python и зависимостей.');
  });
  backendProcess.on('close', (code) => {
    console.log(`Backend exited with code ${code}`);
  });
}

function waitForBackend(timeout = 10000) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    const checkPort = () => {
      const socket = new net.Socket();
      socket.setTimeout(500);
      socket.once('connect', () => {
        socket.destroy();
        resolve();
      });
      socket.once('timeout', () => {
        socket.destroy();
        if (Date.now() - startTime < timeout) {
          setTimeout(checkPort, 200);
        } else {
          reject(new Error('Backend не запустился за отведённое время'));
        }
      });
      socket.once('error', () => {
        socket.destroy();
        if (Date.now() - startTime < timeout) {
          setTimeout(checkPort, 200);
        } else {
          reject(new Error('Backend не запустился за отведённое время'));
        }
      });
      socket.connect(8000, '127.0.0.1');
    };
    checkPort();
  });
}

async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    title: 'Семейный бюджет',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    }
  });

  try {
    await waitForBackend();
    console.log('Бэкенд готов, загружаем фронтенд');

    if (process.env.VITE_DEV_SERVER_URL) {
      await mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL);
      mainWindow.webContents.openDevTools();
    } else {
      await mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'));
    }
  } catch (err) {
    console.error(err.message);
    dialog.showErrorBox('Ошибка', 'Не удалось дождаться запуска бэкенда. Попробуйте перезапустить приложение.');
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(async () => {
  startBackend();
  await waitForBackend();
  await createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  if (backendProcess && !backendProcess.killed) {
    backendProcess.kill('SIGTERM');
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});