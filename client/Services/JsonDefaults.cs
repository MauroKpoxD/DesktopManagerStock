using System.Text.Json;

namespace DesktopManagerStock.Client.Services;

/// <summary>
/// La API (FastAPI/Pydantic) usa snake_case ("stock_minimo", "access_token", ...);
/// los modelos de C# usan PascalCase por convención ("StockMinimo", "AccessToken").
/// JsonNamingPolicy.SnakeCaseLower (agregada en .NET 8) hace esa traducción
/// automáticamente en ambas direcciones, sin necesitar [JsonPropertyName] en
/// cada propiedad de cada modelo.
/// </summary>
public static class JsonDefaults
{
    public static readonly JsonSerializerOptions Options = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
        PropertyNameCaseInsensitive = true,
        DictionaryKeyPolicy = JsonNamingPolicy.SnakeCaseLower,
    };
}
