using Microsoft.Maui.Storage;

namespace DesktopManagerStock.Client.Services;

/// <summary>
/// El login y la animación de arranque se mantienen siempre con el tema
/// oscuro de marca (es una decisión de diseño común: pantallas de bienvenida
/// con identidad fija); este servicio solo controla el contenido de la app
/// una vez logueado (ver el div envolvente en Routes.razor).
/// </summary>
public class ThemeService
{
    private const string PreferenceKey = "tema_claro";

    public bool EsClaro
    {
        get => Preferences.Default.Get(PreferenceKey, false);
        private set => Preferences.Default.Set(PreferenceKey, value);
    }

    public event Action? OnChange;

    public void Alternar()
    {
        EsClaro = !EsClaro;
        OnChange?.Invoke();
    }
}
