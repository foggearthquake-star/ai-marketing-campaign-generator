# Frontend (Next.js + TypeScript)

## English
RU-first workspace UI for AI Campaign MVP.

### Run (stable mode)
```bash
npm install
npm run build
npm run start
```

### Dev mode (optional)
```bash
npm run dev
```

### Required env
- `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000`

### Troubleshooting
- If you see `Cannot find module './xxx.js'`:
  1. stop Node process
  2. remove `.next`
  3. run `npm run build && npm run start`

---

## Русский
RU-first интерфейс workspace для AI Campaign MVP.

### Запуск (стабильный режим)
```bash
npm install
npm run build
npm run start
```

### Dev-режим (опционально)
```bash
npm run dev
```

### Обязательная env-переменная
- `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000`

### Если ошибка `Cannot find module './xxx.js'`
1. остановите Node
2. удалите `.next`
3. запустите `npm run build && npm run start`
