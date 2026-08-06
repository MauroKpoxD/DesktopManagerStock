using Microsoft.Maui.Storage;

namespace DesktopManagerStock.Client.Services;

/// <summary>
/// URL base de la API, configurable desde la pantalla de Perfil/Configuración
/// sin recompilar la app (por ejemplo, para apuntar a un servidor en la red
/// local en vez de http://localhost:8000).
///
/// Nota: como HttpClient.BaseAddress se fija una sola vez al construir el
/// cliente (ver MauiProgram.cs), cambiar este valor requiere reiniciar la
/// app para que tome efecto. Se avisa de esto en la UI (ver Perfil.razor).
/// </summary>
public class ApiSettings
{
    private const string PreferenceKey = "api_base_url";
    private const string DefaultUrl = "http://localhost:8000/api/v1";

    public string BaseUrl
    {
        get
        {
            var value = Preferences.Default.Get(PreferenceKey, DefaultUrl);
            // Asegura que siempre termine en "/" para que las rutas relativas
            // de HttpClient ("productos", "auth/login", etc.) se combinen bien.
            return value.EndsWith('/') ? value : value + "/";
        }
        set => Preferences.Default.Set(PreferenceKey, value.Trim());
    }

    public bool EsValorPorDefecto => BaseUrl.TrimEnd('/') == DefaultUrl.TrimEnd('/');
}
