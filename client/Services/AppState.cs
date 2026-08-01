using DesktopManagerStock.Client.Models;

namespace DesktopManagerStock.Client.Services;

/// <summary>
/// Estado global simple (singleton) con el usuario logueado actual. Los
/// componentes Razor se suscriben a OnChange para re-renderizarse cuando
/// cambia (login, logout, actualización de perfil).
/// </summary>
public class AppState
{
    public Usuario? UsuarioActual { get; private set; }

    public bool EstaAutenticado => UsuarioActual is not null;

    public event Action? OnChange;

    public void EstablecerUsuario(Usuario? usuario)
    {
        UsuarioActual = usuario;
        OnChange?.Invoke();
    }

    public bool EsAdmin => UsuarioActual?.Rol == "admin";
    public bool PuedeEditar => UsuarioActual?.Rol is "admin" or "editor";
}
