import { apiRequest } from "./api";

export function getProducts() {
  return apiRequest("/products/");
}

export function getSuppliers() {
  return apiRequest("/suppliers/");
}

export function getLowStockProducts() {
  return apiRequest("/products/low-stock/");
}

export function getTransactions() {
  return apiRequest("/transactions/");
}

export function receiveStock(data) {
  return apiRequest("/stock/receive/", {
    method: "POST",
    body: data,
  });
}

export function issueStock(data) {
  return apiRequest("/stock/issue/", {
    method: "POST",
    body: data,
  });
}