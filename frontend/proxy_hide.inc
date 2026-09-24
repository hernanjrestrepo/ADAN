# El backend también manda estas cabeceras; nginx las pone para todo el sitio
proxy_hide_header X-Content-Type-Options;
proxy_hide_header X-Frame-Options;
proxy_hide_header Referrer-Policy;
