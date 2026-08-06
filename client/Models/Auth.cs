namespace DesktopManagerStock.Client.Models;

public class TokenResponse
{
    public string AccessToken { get; set; } = string.Empty;
    public string TokenType { get; set; } = "bearer";
    public string? RefreshToken { get; set; }
}

/// <summary>Body para POST /auth/refresh y POST /auth/logout.</summary>
public class RefreshTokenRequest
{
    public string RefreshToken { get; set; } = string.Empty;
}

/// <summary>
/// Forma típica de los errores que devuelve la API: {"detail": "mensaje"}.
/// Para errores de validación de Pydantic, "detail" puede ser una lista de
/// objetos en vez de un string; ApiClient.LeerMensajeDeError maneja ambos casos.
/// </summary>
public class ApiErrorBody
{
    public object? Detail { get; set; }
}

/// <summary>Excepción con el mensaje ya extraído de la respuesta de error de la API.</summary>
public class ApiException : Exception
{
    public int StatusCode { get; }

    public ApiException(int statusCode, string message) : base(message)
    {
        StatusCode = statusCode;
    }
}
