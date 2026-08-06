using System.Net.Http.Json;
using System.Text.Json;
using DesktopManagerStock.Client.Models;

namespace DesktopManagerStock.Client.Services;

public static class ApiHelpers
{
    /// <summary>
    /// Si la respuesta no fue exitosa, arma un mensaje legible a partir del
    /// cuerpo de error de la API y lanza ApiException. La API devuelve
    /// {"detail": "mensaje"} en la mayoría de los casos, pero en errores de
    /// validación de Pydantic "detail" es una lista de objetos
    /// {"loc": [...], "msg": "...", "type": "..."} — se contemplan ambos casos.
    /// </summary>
    public static async Task EnsureSuccessOrThrowAsync(this HttpResponseMessage response)
    {
        if (response.IsSuccessStatusCode) return;

        string mensaje = $"Error {(int)response.StatusCode} ({response.ReasonPhrase})";
        try
        {
            var json = await response.Content.ReadAsStringAsync();
            if (!string.IsNullOrWhiteSpace(json))
            {
                using var doc = JsonDocument.Parse(json);
                if (doc.RootElement.TryGetProperty("detail", out var detail))
                {
                    if (detail.ValueKind == JsonValueKind.String)
                    {
                        mensaje = detail.GetString() ?? mensaje;
                    }
                    else if (detail.ValueKind == JsonValueKind.Array)
                    {
                        var mensajes = new List<string>();
                        foreach (var item in detail.EnumerateArray())
                        {
                            if (item.TryGetProperty("msg", out var msg))
                            {
                                mensajes.Add(msg.GetString() ?? "");
                            }
                        }
                        if (mensajes.Count > 0)
                        {
                            mensaje = string.Join(" | ", mensajes);
                        }
                    }
                }
            }
        }
        catch
        {
            // Si el cuerpo no es JSON válido (por ejemplo, un 502 de un proxy),
            // se conserva el mensaje genérico armado arriba.
        }

        throw new ApiException((int)response.StatusCode, mensaje);
    }

    /// <summary>Lee el header X-Total-Count que agregan los listados paginados (ver server/app/api/routes.py).</summary>
    public static int LeerTotalCount(this HttpResponseMessage response, int fallback)
    {
        if (response.Headers.TryGetValues("X-Total-Count", out var values) &&
            int.TryParse(values.FirstOrDefault(), out var total))
        {
            return total;
        }
        return fallback;
    }
}

/// <summary>Resultado de un listado paginado: los items de esta página + el total real.</summary>
public class PaginaResultado<T>
{
    public List<T> Items { get; set; } = new();
    public int Total { get; set; }
}
