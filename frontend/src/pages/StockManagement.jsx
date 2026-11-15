import { useEffect, useState } from "react";
import {
  getProducts,
  getSuppliers,
  receiveStock,
} from "../services/inventoryService";

import IssueStockForm from "../components/IssueStockForm";

function StockManagement() {
  const [products, setProducts] = useState([]);
  const [suppliers, setSuppliers] = useState([]);

  const [productId, setProductId] = useState("");
  const [supplierId, setSupplierId] = useState("");
  const [quantity, setQuantity] = useState("");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    let ignore = false;

    async function loadOptions() {
      try {
        const [productData, supplierData] = await Promise.all([
          getProducts(),
          getSuppliers(),
        ]);

        if (!ignore) {
          setProducts(productData);
          setSuppliers(supplierData);
        }
      } catch (error) {
        if (!ignore) {
          setLoadError(error.message);
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }

    loadOptions();

    return () => {
      ignore = true;
    };
  }, []);

  const selectedProduct = products.find(
    (product) => product.id === Number(productId)
  );

  async function refreshProducts() {
  const updatedProducts = await getProducts();
  setProducts(updatedProducts);
  }

  async function handleReceive(event) {
    event.preventDefault();
    setError("");
    setSuccess("");

    const amount = Number(quantity);

    if (!productId || !supplierId) {
      setError("Please select a product and supplier.");
      return;
    }

    if (!Number.isSafeInteger(amount) || amount <= 0) {
      setError("Quantity must be a positive whole number.");
      return;
    }

    setSaving(true);

    try {
      const transaction = await receiveStock({
        product: Number(productId),
        supplier: Number(supplierId),
        quantity: amount,
      });

      setSuccess(
        `Received ${transaction.quantity} units successfully. ` +
        `Transaction ID: ${transaction.id}.`
      );

      setQuantity("");

      try {
        const updatedProducts = await getProducts();
        setProducts(updatedProducts);
      } catch {
        setError(
          "Stock was received, but the latest stock could not be loaded. " +
          "Reload the page to check it. Do not submit the same receipt again."
        );
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="card">
      <h2>Stock Management</h2>
      <p>Record stock received from suppliers and stock issued from inventory.</p>

      {loading && <p role="status">Loading products and suppliers...</p>}

      {loadError && (
        <p className="error-message" role="alert">
          {loadError}
        </p>
      )}

      {!loading && !loadError && (
        <>
          <h3>Receive Stock</h3>

          {products.length === 0 || suppliers.length === 0 ? (
            <p>
              A product and supplier must exist before stock can be received.
              Add the missing records through Django admin.
            </p>
          ) : (
            <form onSubmit={handleReceive} className="form">
              <label htmlFor="receive-product">Product</label>
              <select
                id="receive-product"
                value={productId}
                onChange={(event) => setProductId(event.target.value)}
                disabled={saving}
                required
              >
                <option value="">Select a product</option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.product_name} ({product.sku})
                  </option>
                ))}
              </select>

              {selectedProduct && (
                <p>
                  Current stock:{" "}
                  <strong>{selectedProduct.stock_quantity}</strong>
                </p>
              )}

              <label htmlFor="receive-supplier">Supplier</label>
              <select
                id="receive-supplier"
                value={supplierId}
                onChange={(event) => setSupplierId(event.target.value)}
                disabled={saving}
                required
              >
                <option value="">Select a supplier</option>
                {suppliers.map((supplier) => (
                  <option key={supplier.id} value={supplier.id}>
                    {supplier.supplier_name}
                  </option>
                ))}
              </select>

              <label htmlFor="receive-quantity">Quantity</label>
              <input
                id="receive-quantity"
                type="number"
                min="1"
                step="1"
                value={quantity}
                onChange={(event) => setQuantity(event.target.value)}
                disabled={saving}
                required
              />

              <button type="submit" disabled={saving}>
                {saving ? "Receiving..." : "Receive Stock"}
              </button>
            </form>
          )}
        </>
      )}

      {success && (
        <p className="success-message" role="status">
          {success}
        </p>
      )}

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {!loading && !loadError && (
      <IssueStockForm
       products={products}
      onStockUpdated={refreshProducts}
       />
)}
    </section>
  );
}

export default StockManagement;