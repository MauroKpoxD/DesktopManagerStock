using Microsoft.Extensions.Logging;
using DesktopManagerStock.Client.Services;

namespace DesktopManagerStock.Client;

public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .UseMauiApp<App>()
            .ConfigureFonts(fonts =>
            {
                // Sin fuentes personalizadas por defecto: se usa la fuente del
                // sistema operativo. Si querés una tipografía propia, agregá el
                // .ttf en Resources/Fonts y regístralo acá con fonts.AddFont(...).
            });

        builder.Services.AddMauiBlazorWebView();

#if DEBUG
        builder.Services.AddBlazorWebViewDeveloperTools();
#endif

        // --- Configuración de la API ---
        // La URL base se guarda en Preferences (ver Services/ApiSettings.cs) para
        // que se pueda cambiar desde la pantalla de Configuración sin recompilar
        // (por ejemplo, para apuntar a un servidor en la red en vez de localhost).
        builder.Services.AddSingleton<ApiSettings>();
        builder.Services.AddSingleton<AuthTokenStore>();
        builder.Services.AddSingleton<AppState>();
        builder.Services.AddSingleton<NavigationState>();
        builder.Services.AddSingleton<ToastService>();
        builder.Services.AddSingleton<AlertaStockService>();
        builder.Services.AddSingleton<ThemeService>();

        // AuthDelegatingHandler intercepta cada request: agrega el
        // Authorization: Bearer <token> y, si la respuesta es 401, intenta
        // renovar el access_token con el refresh_token antes de reintentar.
        builder.Services.AddTransient<AuthDelegatingHandler>();

        builder.Services.AddHttpClient<AuthService>((sp, client) =>
        {
            var settings = sp.GetRequiredService<ApiSettings>();
            client.BaseAddress = new Uri(settings.BaseUrl);
        });

        builder.Services.AddHttpClient("ApiConAuth", (sp, client) =>
        {
            var settings = sp.GetRequiredService<ApiSettings>();
            client.BaseAddress = new Uri(settings.BaseUrl);
        }).AddHttpMessageHandler<AuthDelegatingHandler>();

        builder.Services.AddTransient<ProductoService>();
        builder.Services.AddTransient<MovimientoService>();
        builder.Services.AddTransient<UsuarioService>();
        builder.Services.AddTransient<ReporteService>();
        builder.Services.AddTransient<PerfilService>();

        return builder.Build();
    }
}
