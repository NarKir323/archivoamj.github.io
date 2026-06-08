# Archivo AMJ

Sitio personal de divulgación histórica con dos áreas principales:

- **Archivo Militar:** mapa narrativo de la campaña insurgente.
- **Archivo de escritos:** catálogo temático de ensayos adaptados para lectura web.

## Publicación

El sitio se publica mediante GitHub Pages desde la rama `main`.

Antes de subir cambios:

```powershell
python scripts/validate_site.py
```

Después:

```powershell
git add .
git commit -m "Actualizar Archivo AMJ"
git push origin main
```

La acción **Validar sitio** repite automáticamente la revisión en cada `push`,
en cada pull request y semanalmente.

## Seguridad

El sitio es estático y no procesa formularios, cuentas, pagos ni datos de
visitantes. Cada página aplica una Content Security Policy restrictiva y la
validación automática rechaza scripts en línea, enlaces externos inseguros y
referencias locales rotas.

Los reportes de seguridad deben seguir [SECURITY.md](SECURITY.md).
