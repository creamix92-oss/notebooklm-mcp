# Automatización gratuita de la campaña (YouTube)

## Qué hace
- **Publica solo lo que apruebas** en `cola.json` (`aprobado: true` y fecha vencida, en UTC; 19:00 de Santo Domingo = 23:00 UTC): añade tu texto de escucha a la descripción de una canción tuya (`set_description`) o sube un clip propio (`upload_short`).
- **Mide cada lunes** (YouTube Analytics) y separa vistas de clips de vistas de canciones completas en `metricas.csv` e `informe_ultimo.md`.
- Corre gratis en GitHub Actions (`.github/workflows/campana-musical.yml`), cada hora.

## Protecciones
Modo simulación por defecto. Comprueba que el canal autenticado es el correcto. No repite nada que ya se publicó o quedó ambiguo (revisa el historial antes). Un bloqueo se registra una sola vez. No usa contraseñas ni OTP: solo OAuth.

## Qué NO puede hacer (límite de YouTube)
La API **no permite crear publicaciones de la pestaña Comunidad**, así que esas se quedan como borradores manuales (`calendario_4_semanas.md`). Tampoco hay API para otras redes en este paquete.

## Puesta en marcha (una vez, ~15 min, en TU ordenador)
1. Google Cloud (gratis) → proyecto nuevo → activar *YouTube Data API v3* y *YouTube Analytics API* → pantalla de consentimiento (tú como usuario de prueba) → credenciales **ID de cliente OAuth tipo "Aplicación de escritorio"**.
2. `python yt_campaign.py authorize byrabit` e inicia sesión con la cuenta PROPIETARIA del canal. Repite con `taquitos` solo cuando verifiques su administración y pongas `admin_verificada: true` en `config.json`.
3. En GitHub → Settings → Secrets → Actions, guarda `YT_BYRABIT_CLIENT_ID`, `YT_BYRABIT_CLIENT_SECRET`, `YT_BYRABIT_REFRESH_TOKEN` (y los de TAQUITOS). **No los pegues en chats.**
4. Combina el PR en la rama por defecto (los cron solo corren ahí). Ejecuta el workflow a mano con "Run workflow" y mira que `check` diga OK.
5. Para activar la escritura real: Settings → Variables → `CAMPANA_LIVE` = `true`. Sin eso solo simula.
6. Edita `cola.json`, pon `aprobado: true`, y se ejecutará a su hora.

Si el proyecto de Google queda en modo "Prueba", el token caduca a los 7 días; publícalo (modo "En producción") para uso propio.

## Estado de verificación
Probado con simulaciones locales (5 pruebas, pasan). **No** se ha probado contra la API real de YouTube, porque no hay credenciales en este entorno.
