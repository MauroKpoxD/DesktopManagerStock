using System.Net;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using DesktopManagerStock.Client.Models;

namespace DesktopManagerStock.Client.Services;

/// <summary>
/// Se engancha en el HttpClient "ApiConAuth" (ver MauiProgram.cs). En cada
/// request:
///   1. Agrega "Authorization: Bearer {access_token}" si hay uno en memoria.
///   2. Si la respuesta es 401, intenta renovar el access_token usando el
///      refresh_token guardado en SecureStorage, y reintenta la request UNA
///      vez con el token nuevo.
///   3. Si la renovación también falla (refresh_token vencido o revocado),
///      limpia la sesión y notifica a AppState para que la UI vuelva al login.
///
/// Un SemaphoreSlim evita que múltiples requests en paralelo disparen
/// renovaciones simultáneas (todas esperan a la primera y reusan su resultado).
/// </summary>
public class AuthDelegatingHandler : DelegatingHandler
{
    private readonly AuthTokenStore _tokenStore;
    private readonly ApiSettings _apiSettings;
    private readonly AppState _appState;
    private readonly ToastService _toastService;
    private static readonly SemaphoreSlim _refreshLock = new(1, 1);

    public AuthDelegatingHandler(AuthTokenStore tokenStore, ApiSettings apiSettings, AppState appState, ToastService toastService)
    {
        _tokenStore = tokenStore;
        _apiSettings = apiSettings;
        _appState = appState;
        _toastService = toastService;
    }

    protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
    {
        AplicarToken(request);
        var response = await base.SendAsync(request, cancellationToken);

        if (response.StatusCode != HttpStatusCode.Unauthorized)
        {
            return response;
        }

        // Evita reintentar infinitamente el propio endpoint de refresh si ese
        // es el que devolvió 401 (refresh_token vencido/revocado).
        if (request.RequestUri?.AbsolutePath.Contains("/auth/refresh") == true)
        {
            CerrarSesionPorTokenInvalido();
            return response;
        }

        var renovado = await IntentarRenovarTokenAsync();
        if (!renovado)
        {
            CerrarSesionPorTokenInvalido();
            return response;
        }

        // Reintenta la request original una sola vez con el token nuevo.
        // HttpRequestMessage no se puede reenviar tal cual (ya fue consumido),
        // así que se clona.
        var requestClonado = await ClonarRequestAsync(request);
        AplicarToken(requestClonado);
        response.Dispose();
        return await base.SendAsync(requestClonado, cancellationToken);
    }

    private void AplicarToken(HttpRequestMessage request)
    {
        if (!string.IsNullOrEmpty(_tokenStore.AccessToken))
        {
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", _tokenStore.AccessToken);
        }
    }

    private async Task<bool> IntentarRenovarTokenAsync()
    {
        await _refreshLock.WaitAsync();
        try
        {
            var refreshToken = await _tokenStore.ObtenerRefreshTokenAsync();
            if (string.IsNullOrEmpty(refreshToken))
            {
                return false;
            }

            using var client = new HttpClient { BaseAddress = new Uri(_apiSettings.BaseUrl) };
            var response = await client.PostAsJsonAsync("auth/refresh", new RefreshTokenRequest { RefreshToken = refreshToken }, JsonDefaults.Options);
            if (!response.IsSuccessStatusCode)
            {
                return false;
            }

            var token = await response.Content.ReadFromJsonAsync<TokenResponse>(JsonDefaults.Options);
            if (token is null || string.IsNullOrEmpty(token.AccessToken))
            {
                return false;
            }

            await _tokenStore.GuardarAsync(token.AccessToken, token.RefreshToken);
            return true;
        }
        catch
        {
            // Sin conexión, timeout, etc.: se trata igual que una renovación fallida.
            return false;
        }
        finally
        {
            _refreshLock.Release();
        }
    }

    private void CerrarSesionPorTokenInvalido()
    {
        // Antes esto pasaba en silencio: el usuario quedaba mirando la
        // pantalla de login sin saber por qué "se lo echó" en medio de un
        // uso normal de la app. Ahora se avisa el motivo.
        var estabaAutenticado = _appState.EstaAutenticado;
        _tokenStore.LimpiarSesion();
        _appState.EstablecerUsuario(null);
        if (estabaAutenticado)
        {
            _toastService.Info("Tu sesión expiró. Iniciá sesión de nuevo.");
        }
    }

    private static async Task<HttpRequestMessage> ClonarRequestAsync(HttpRequestMessage original)
    {
        var clone = new HttpRequestMessage(original.Method, original.RequestUri);
        if (original.Content is not null)
        {
            var bytes = await original.Content.ReadAsByteArrayAsync();
            clone.Content = new ByteArrayContent(bytes);
            foreach (var header in original.Content.Headers)
            {
                clone.Content.Headers.TryAddWithoutValidation(header.Key, header.Value);
            }
        }
        foreach (var header in original.Headers)
        {
            clone.Headers.TryAddWithoutValidation(header.Key, header.Value);
        }
        return clone;
    }
}
