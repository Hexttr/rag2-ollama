# Решение проблемы с VPN

## Проблема

- С VPN: проблемы с локальными подключениями (Ollama, Backend)
- Без VPN: не работает интернет

## Решение

### 1. Отключите VPN через приложение

Закройте VPN приложение полностью (не просто отключите, а закройте).

### 2. Отключите VPN адаптеры вручную

**Через PowerShell (запустите от администратора):**
```powershell
# Найти VPN адаптеры
Get-NetAdapter | Where-Object {$_.InterfaceDescription -like "*TAP*"}

# Отключить их
Disable-NetAdapter -Name "Имя_адаптера" -Confirm:$false
```

**Или через GUI:**
1. Откройте "Сетевые подключения" (ncpa.cpl)
2. Найдите VPN адаптеры (TAP, OpenVPN и т.д.)
3. Правый клик → Отключить

### 3. Настройте DNS

После отключения VPN, если интернет не работает:

```bash
# Очистить DNS кэш
ipconfig /flushdns

# Установить DNS Google
netsh interface ip set dns "Ethernet" static 8.8.8.8
netsh interface ip add dns "Ethernet" 8.8.4.4 index=2
```

### 4. Проверьте интернет

```bash
ping google.com
ping 8.8.8.8
```

## Альтернативное решение

Если нужно оставить VPN включенным:

1. **Настройте VPN для локальных подключений:**
   - Отключите "Kill Switch"
   - Отключите "Block local network"
   - Добавьте исключения для 127.0.0.1 и localhost

2. **Используйте split tunneling:**
   - Настройте VPN так, чтобы локальный трафик не проходил через VPN

## Готовность

✅ **Следуйте инструкциям выше для решения проблемы с VPN**

После отключения VPN проверьте работу Ollama и Backend.


