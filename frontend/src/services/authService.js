import { apiRequest } from "./api";

export async function login(username, password) {
  const data = await apiRequest("/token/", {
    method: "POST",
    body: { username, password },
    authenticated: false,
  });

  if (!data?.token) {
    throw new Error("Login response did not contain a token.");
  }

  sessionStorage.setItem("token", data.token);
}

export function logout() {
  sessionStorage.removeItem("token");
}