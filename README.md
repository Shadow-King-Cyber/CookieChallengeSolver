# CookieChallengeSolver

Script en Python que resuelve automáticamente retos CTF de tipo *cookie* de la plataforma [hackrocks](https://challenges.hackrocks.com/) (y otros similares).

## ¿De qué trata el reto?

En estos desafíos, el servidor envía cookies revelando las credenciales (o pistas sobre ellas) al visitar la página sin estar autenticado. Por ejemplo, en el reto **"Wanna some cookies"** el servidor responde con un `Set-Cookie` como este:

```
User=cookieChef, Password=doYouLikeRaisins, Rol=Admin, ...
```

El script automatiza el proceso completo:

1. Realiza un `GET` a la URL del reto y lee el header `Set-Cookie`.
2. Busca campos de usuario/contraseña dentro de las cookies.
3. Descarga los archivos JS referenciados por la página para localizar el formulario de login (que suele generarse dinámicamente).
4. Envía las credenciales encontradas al endpoint de login (`check_pass`, etc.).
5. Extrae e imprime el token de éxito de la respuesta.

## Requisitos

- Python 3.6+
- Librería `requests`

Instalación de la dependencia:

```bash
pip install requests
```

## Uso

Ejecutar contra el reto por defecto:

```bash
python cookie_challenge_solver.py
```

Ejecutar contra otra URL:

```bash
python cookie_challenge_solver.py https://challenges.hackrocks.com/otro-reto
```

### Ejemplo de salida

```
[*] GET https://challenges.hackrocks.com/wanna-some-cookies -> 200
[*] Cookies recibidas por el servidor:
    Log_time=15days
    Password=doYouLikeRaisins
    Rol=Admin
    Sesion=Sesion_Rasin_2019_02_10
    Signature=...
    Status=Loged
    User=cookieChef
[*] Formulario de login detectado: https://challenges.hackrocks.com/wanna-some-cookies/check_pass
[*] Probando credenciales -> user: cookieChef | password: doYouLikeRaisins
[*] POST https://challenges.hackrocks.com/wanna-some-cookies/check_pass -> 200

[+] TOKEN / FLAG: PasswordInMyCookies?!
```

## Aviso legal

Esta herramienta está pensada **únicamente** para fines educativos y para resolver retos de plataformas de seguridad autorizadas (CTF, laboratorios de pentesting). No la utilices contra sistemas sin autorización explícita.

## Licencia

[MIT](LICENSE)