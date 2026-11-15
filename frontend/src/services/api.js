const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function apiRequest(
  endpoint,
  { method = "GET", body, authenticated = true } = {}
) {
  const headers = {
    Accept: "application/json",
  };

  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  const token = sessionStorage.getItem("token");

  if (authenticated && token) {
    headers.Authorization = `Token ${token}`;
  }

  let response;

  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new Error(
      "Cannot connect to the server. Check your connection and try again."
    );
  }

  const text = await response.text();
  let data = null;

  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      throw new Error("The server returned an unexpected response.");
    }
  }

  if (!response.ok) {
  let message = `Request failed (${response.status}). Please try again.`;

  if (data && typeof data === "object") {
    message = Object.entries(data)
      .map(([field, errors]) => {
        const text = Array.isArray(errors)
          ? errors.join(" ")
          : String(errors);

        return field === "detail" || field === "non_field_errors"
          ? text
          : `${field}: ${text}`;
      })
      .join(" ");
  }

  throw new Error(message);
}

  return data;
}